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

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db_session
from app.core.security import get_password_hash
from app.models.log import Log
from app.models.user import User, UserRole
from app.schemas.admin import LogOut, UserCreate, UserOut, UserUpdate

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin, UserRole.moderator])),
) -> list[UserOut]:
    result = await db.execute(select(User).order_by(User.id.asc()))
    return [UserOut.model_validate(user, from_attributes=True) for user in result.scalars().all()]


@router.post("/users", response_model=UserOut)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> UserOut:
    user = User(
        login=payload.login,
        password_hash=get_password_hash(payload.password),
        role=UserRole(payload.role),
        full_name=payload.full_name,
        department=payload.department,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user, from_attributes=True)


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> UserOut:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.role:
        user.role = UserRole(payload.role)
    if payload.department is not None:
        user.department = payload.department
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password:
        user.password_hash = get_password_hash(payload.password)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user, from_attributes=True)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict[str, str]:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"status": "blocked"}


@router.get("/logs", response_model=list[LogOut])
async def list_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> list[LogOut]:
    result = await db.execute(select(Log).order_by(desc(Log.timestamp)).limit(limit))
    return [LogOut.model_validate(row, from_attributes=True) for row in result.scalars().all()]
