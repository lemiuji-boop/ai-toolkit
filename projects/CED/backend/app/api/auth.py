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

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse, RefreshRequest, TokenPair, UserMeOut
from app.services.auth_service import authenticate_user, build_token_pair, decode_refresh_token
from app.services.presence_service import touch_presence
from app.services.rate_limit_service import check_login_allowed, register_login_failure, reset_login_rate_limit

router = APIRouter()


def _client_key(request: Request, login: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{host}:{login.lower()}"


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    key = _client_key(request, payload.login)
    await check_login_allowed(key)
    try:
        user = await authenticate_user(db, payload.login, payload.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            await register_login_failure(key)
        raise
    await reset_login_rate_limit(key)
    tokens = build_token_pair(str(user.id))
    return LoginResponse(**tokens, must_change_password=bool(user.must_change_password))


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest) -> TokenPair:
    subject = decode_refresh_token(payload.refresh_token)
    return TokenPair(**build_token_pair(subject))


@router.get("/me", response_model=UserMeOut)
async def me(current_user: User = Depends(get_current_user)) -> UserMeOut:
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    await touch_presence(current_user.id, current_user.login, role)
    return UserMeOut.model_validate(current_user, from_attributes=True)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль")
    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.must_change_password = False
    await db.commit()
    return {"status": "ok"}


@router.post("/heartbeat")
async def heartbeat(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    await touch_presence(current_user.id, current_user.login, role)
    return {"status": "ok"}
