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

"""REST API мобильного клиента."""

from __future__ import annotations

import json
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import LaborRecordStore, MobileUser, UserSession
from app.services.activity import log_activity
from app.services.security import verify_password
from app.services.seed import DEFAULT_OPERATIONS

router = APIRouter(prefix="/api/v1/mobile", tags=["mobile"])

VALID_DEVICE_TOKENS = {"dev-device-token", "staging-token"}


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    display_name: str
    tab_number: str = ""
    expires_in: int = 86_400


class UserProfileOut(BaseModel):
    username: str
    display_name: str
    tab_number: str = ""


class LaborRecordIn(BaseModel):
    client_id: str
    date: str
    worker: str
    product: str
    operation: str
    value: float = Field(gt=0)
    unit: str
    note: str = ""


class BatchPushRequest(BaseModel):
    records: list[LaborRecordIn]


class AcceptedRecord(BaseModel):
    client_id: str
    server_id: str


class BatchError(BaseModel):
    client_id: str
    message: str


class BatchPushResponse(BaseModel):
    accepted: list[AcceptedRecord]
    errors: list[BatchError] = Field(default_factory=list)


class OperationOut(BaseModel):
    id: int
    name: str
    active: bool = True


def _session_user(db: Session, token: str) -> MobileUser | None:
    row = db.query(UserSession).filter(UserSession.token == token).first()
    if not row:
        return None
    return db.get(MobileUser, row.user_id)


def verify_token(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> tuple[str, MobileUser | None]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token in VALID_DEVICE_TOKENS:
        return token, None
    user = _session_user(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный или просроченный токен")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Учётная запись заблокирована")
    return token, user


@router.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    login_key = body.username.strip().lower()
    user = db.query(MobileUser).filter(MobileUser.username == login_key).first()
    if user is None or not verify_password(body.password, user.password_hash):
        log_activity(db, action="login_failed", detail=login_key, username=login_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    if user.is_blocked:
        log_activity(db, action="login_blocked", user_id=user.id, username=user.username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Учётная запись заблокирована")

    token = f"usr-{secrets.token_urlsafe(24)}"
    db.add(UserSession(token=token, user_id=user.id))
    log_activity(db, action="login", user_id=user.id, username=user.username)
    db.commit()
    return LoginResponse(
        access_token=token,
        display_name=user.display_name,
        tab_number=user.tab_number or "",
    )


@router.get("/auth/me", response_model=UserProfileOut)
async def current_user(
    auth: tuple[str, MobileUser | None] = Depends(verify_token),
) -> UserProfileOut:
    _, user = auth
    if user is not None:
        return UserProfileOut(
            username=user.username,
            display_name=user.display_name,
            tab_number=user.tab_number or "",
        )
    return UserProfileOut(username="device", display_name="Устройство (dev)", tab_number="")


@router.post("/auth/logout")
async def logout(
    auth: tuple[str, MobileUser | None] = Depends(verify_token),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    token, user = auth
    db.query(UserSession).filter(UserSession.token == token).delete()
    if user:
        log_activity(db, action="logout", user_id=user.id, username=user.username)
    db.commit()
    return {"status": "ok"}


@router.get("/operations", response_model=list[OperationOut])
async def list_operations(_: tuple[str, MobileUser | None] = Depends(verify_token)) -> list[OperationOut]:
    return [OperationOut(id=i + 1, name=name) for i, name in enumerate(DEFAULT_OPERATIONS)]


@router.post("/labor-records/batch", response_model=BatchPushResponse)
async def push_batch(
    body: BatchPushRequest,
    auth: tuple[str, MobileUser | None] = Depends(verify_token),
    db: Session = Depends(get_db),
) -> BatchPushResponse:
    token, user = auth
    accepted: list[AcceptedRecord] = []
    errors: list[BatchError] = []
    count = db.query(LaborRecordStore).count()

    for record in body.records:
        if record.value <= 0:
            errors.append(BatchError(client_id=record.client_id, message="value must be > 0"))
            continue
        existing = db.get(LaborRecordStore, record.client_id)
        if existing:
            server_id = existing.server_id
        else:
            count += 1
            server_id = f"srv-{count}"
            db.add(
                LaborRecordStore(
                    client_id=record.client_id,
                    server_id=server_id,
                    user_id=user.id if user else None,
                    payload_json=record.model_dump_json(),
                )
            )
        accepted.append(AcceptedRecord(client_id=record.client_id, server_id=server_id))

    if user and accepted:
        log_activity(
            db,
            action="sync_batch",
            user_id=user.id,
            username=user.username,
            detail=f"{len(accepted)} записей",
        )
    db.commit()
    return BatchPushResponse(accepted=accepted, errors=errors)
