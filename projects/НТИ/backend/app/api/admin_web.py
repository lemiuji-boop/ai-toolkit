# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Веб-админка: пользователи, API, Ollama, токены, журнал."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ActivityLog, ApiService, MobileUser, OllamaModel, SystemSetting, TokenUsage
from app.services.activity import log_activity
from app.services.ollama import check_ollama_usage, get_setting, list_ollama_tags
from app.services.security import hash_password, verify_password

router = APIRouter(tags=["admin"])

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Сессии админов: token -> username
_ADMIN_SESSIONS: dict[str, str] = {}


def _fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%d.%m.%Y %H:%M")


def _render(request: Request, name: str, context: dict, *, show_nav: bool = True) -> HTMLResponse:
    ctx = {"show_nav": show_nav, **context}
    return templates.TemplateResponse(request, f"admin/{name}", ctx)


def require_admin(admin_token: Annotated[str | None, Cookie()] = None) -> str:
    if not admin_token or admin_token not in _ADMIN_SESSIONS:
        raise RedirectResponse(url="/admin/login", status_code=303)
    return _ADMIN_SESSIONS[admin_token]


def get_admin_or_redirect(admin_token: Annotated[str | None, Cookie()] = None) -> str | RedirectResponse:
    if not admin_token or admin_token not in _ADMIN_SESSIONS:
        return RedirectResponse(url="/admin/login", status_code=303)
    return _ADMIN_SESSIONS[admin_token]


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request) -> HTMLResponse:
    return _render(request, "login.html", {}, show_nav=False)


@router.post("/admin/login")
async def admin_login_post(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
) -> RedirectResponse:
    from app.db.models import AdminUser

    admin = db.query(AdminUser).filter(AdminUser.username == username.strip()).first()
    if admin is None or not verify_password(password, admin.password_hash):
        return RedirectResponse("/admin/login?error=1", status_code=303)
    token = secrets.token_urlsafe(32)
    _ADMIN_SESSIONS[token] = admin.username
    log_activity(db, action="admin_login", username=admin.username)
    response = RedirectResponse("/admin/", status_code=303)
    response.set_cookie("admin_token", token, httponly=True, max_age=86_400)
    return response


@router.get("/admin/logout")
async def admin_logout(admin_token: Annotated[str | None, Cookie()] = None) -> RedirectResponse:
    if admin_token:
        _ADMIN_SESSIONS.pop(admin_token, None)
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("admin_token")
    return response


@router.get("/admin/", response_class=HTMLResponse, response_model=None)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    tokens_week = (
        db.query(func.coalesce(func.sum(TokenUsage.total_tokens), 0))
        .filter(TokenUsage.created_at >= week_ago)
        .scalar()
    )
    recent = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(15).all()
    for row in recent:
        row.created_at = _fmt_dt(row.created_at)

    return _render(
        request,
        "dashboard.html",
        {
            "users_count": db.query(MobileUser).count(),
            "blocked_count": db.query(MobileUser).filter(MobileUser.is_blocked.is_(True)).count(),
            "tokens_week": int(tokens_week or 0),
            "recent_activity": recent,
        },
    )


@router.get("/admin/users", response_class=HTMLResponse, response_model=None)
async def admin_users_page(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    users = db.query(MobileUser).order_by(MobileUser.id).all()
    return _render(request, "users.html", {"users": users})


@router.post("/admin/users")
async def admin_users_create(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    display_name: Annotated[str, Form()],
    tab_number: Annotated[str, Form()] = "",
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    key = username.strip().lower()
    if db.query(MobileUser).filter(MobileUser.username == key).first():
        return RedirectResponse("/admin/users?err=exists", status_code=303)
    db.add(
        MobileUser(
            username=key,
            password_hash=hash_password(password),
            display_name=display_name.strip(),
            tab_number=tab_number.strip(),
        )
    )
    log_activity(db, action="user_created", detail=key, username=str(admin))
    db.commit()
    return RedirectResponse("/admin/users", status_code=303)


@router.post("/admin/users/{user_id}/toggle-block")
async def admin_users_toggle(
    user_id: int,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    user = db.get(MobileUser, user_id)
    if user:
        user.is_blocked = not user.is_blocked
        log_activity(
            db,
            action="user_blocked" if user.is_blocked else "user_unblocked",
            user_id=user.id,
            username=user.username,
        )
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)


@router.post("/admin/users/{user_id}/delete")
async def admin_users_delete(
    user_id: int,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    user = db.get(MobileUser, user_id)
    if user:
        log_activity(db, action="user_deleted", detail=user.username, username=str(admin))
        db.delete(user)
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)


@router.get("/admin/activity", response_class=HTMLResponse, response_model=None)
async def admin_activity_page(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(200).all()
    for row in logs:
        row.created_at = _fmt_dt(row.created_at)
    return _render(request, "activity.html", {"logs": logs})


@router.get("/admin/settings", response_class=HTMLResponse, response_model=None)
async def admin_settings_page(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    return _render(
        request,
        "settings.html",
        {
            "ollama_base_url": get_setting(db, "ollama_base_url"),
            "mobile_public_url": get_setting(db, "mobile_public_url"),
            "ollama_models": db.query(OllamaModel).order_by(OllamaModel.model_name).all(),
            "api_services": db.query(ApiService).order_by(ApiService.id).all(),
        },
    )


@router.post("/admin/settings/ollama")
async def admin_save_ollama(
    ollama_base_url: Annotated[str, Form()],
    active_ollama_model: Annotated[str, Form()],
    mobile_public_url: Annotated[str, Form()] = "",
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    for key, val in [
        ("ollama_base_url", ollama_base_url.strip()),
        ("active_ollama_model", active_ollama_model.strip()),
        ("mobile_public_url", mobile_public_url.strip()),
    ]:
        row = db.get(SystemSetting, key)
        if row:
            row.value = val
        else:
            db.add(SystemSetting(key=key, value=val))
    for model_row in db.query(OllamaModel).all():
        model_row.is_active = False
    active = db.query(OllamaModel).filter(OllamaModel.model_name == active_ollama_model).first()
    if active:
        active.is_active = True
    db.commit()
    return RedirectResponse("/admin/settings", status_code=303)


@router.post("/admin/settings/ollama/sync")
async def admin_sync_ollama_models(
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    names = list_ollama_tags(db)
    for name in names:
        if not db.query(OllamaModel).filter(OllamaModel.model_name == name).first():
            db.add(OllamaModel(model_name=name, is_active=False))
    db.commit()
    return RedirectResponse("/admin/settings", status_code=303)


@router.post("/admin/settings/api/new")
async def admin_api_new(
    name: Annotated[str, Form()],
    base_url: Annotated[str, Form()],
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    db.add(ApiService(name=name.strip(), base_url=base_url.strip()))
    db.commit()
    return RedirectResponse("/admin/settings", status_code=303)


@router.post("/admin/settings/api/{service_id}")
async def admin_api_update(
    service_id: int,
    base_url: Annotated[str, Form()],
    api_key: Annotated[str, Form()] = "",
    description: Annotated[str, Form()] = "",
    enabled: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin
    svc = db.get(ApiService, service_id)
    if svc:
        svc.base_url = base_url.strip()
        svc.api_key = api_key
        svc.description = description
        svc.enabled = enabled == "on"
        db.commit()
    return RedirectResponse("/admin/settings", status_code=303)


@router.get("/admin/tokens", response_class=HTMLResponse, response_model=None)
async def admin_tokens_page(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Annotated[str | None, Cookie()] = None,
    check: str | None = None,
) -> Response:
    admin = get_admin_or_redirect(admin_token)
    if isinstance(admin, RedirectResponse):
        return admin

    summary_rows = (
        db.query(
            TokenUsage.model_name,
            func.count(TokenUsage.id),
            func.coalesce(func.sum(TokenUsage.total_tokens), 0),
        )
        .group_by(TokenUsage.model_name)
        .all()
    )
    summary = [
        {"model_name": m, "count": c, "total": int(t)} for m, c, t in summary_rows
    ]
    recent = db.query(TokenUsage).order_by(TokenUsage.created_at.desc()).limit(50).all()
    for row in recent:
        row.created_at = _fmt_dt(row.created_at)

    check_result = None
    if check == "1":
        check_result = check_ollama_usage(db, admin_username=str(admin))

    return _render(
        request,
        "tokens.html",
        {"summary": summary, "recent": recent, "check_result": check_result},
    )


@router.post("/admin/tokens/check")
async def admin_tokens_check(
    admin_token: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    if not admin_token or admin_token not in _ADMIN_SESSIONS:
        return RedirectResponse("/admin/login", status_code=303)
    return RedirectResponse("/admin/tokens?check=1", status_code=303)
