"""Аутентификация (T-16, контракт §4): POST /api/auth/login → {token}.

Учётные данные администратора — env ADMIN_USER/ADMIN_PASSWORD (начальный режим;
таблица users задействуется при полном T-16). Защита /api/admin/* — Depends(require_admin).
"""
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services import sessions

router = APIRouter(prefix="/api/auth", tags=["auth"])

_bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> LoginResponse:
    """Вход администратора: сверка с env-учёткой, выпуск JWT (TTL из настроек)."""
    if not settings.admin_password:
        # Учётка не настроена — вход явно отключён, а не «пускаем всех».
        raise HTTPException(status_code=503, detail="AUTH_DISABLED: задайте ADMIN_PASSWORD")
    user_ok = secrets.compare_digest(req.username, settings.admin_user)
    pass_ok = secrets.compare_digest(req.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return LoginResponse(token=sessions.issue_token(req.username))


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    """Зависимость защиты /api/admin/*: Bearer JWT обязателен, иначе 401."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация (Bearer JWT)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return sessions.verify_token(credentials.credentials)
    except sessions.TokenError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
