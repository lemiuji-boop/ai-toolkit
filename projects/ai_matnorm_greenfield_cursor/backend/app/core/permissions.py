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

from enum import Enum
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_subject_from_token
from app.db.models import Permission, RolePermission, User, UserRole, UserStatus
from app.db.session import get_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)


class Perm(str, Enum):
    PROJECTS_READ = "projects:read"
    PROJECTS_WRITE = "projects:write"
    CALCULATIONS_WRITE = "calculations:write"
    CALCULATIONS_APPROVE = "calculations:approve"
    FILES_UPLOAD = "files:upload"
    ADMIN = "admin:all"
    DEMO_READ = "demo:read"


ROLE_PERMISSIONS: dict[str, list[str]] = {
    "guest": [Perm.DEMO_READ.value, Perm.PROJECTS_READ.value],
    "technologist": [
        Perm.PROJECTS_READ.value,
        Perm.PROJECTS_WRITE.value,
        Perm.CALCULATIONS_WRITE.value,
        Perm.FILES_UPLOAD.value,
    ],
    "senior_technologist": [
        Perm.PROJECTS_READ.value,
        Perm.PROJECTS_WRITE.value,
        Perm.CALCULATIONS_WRITE.value,
        Perm.CALCULATIONS_APPROVE.value,
        Perm.FILES_UPLOAD.value,
    ],
    "administrator": [p.value for p in Perm],
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")
    try:
        user_id = get_subject_from_token(credentials.credentials, "access")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен") from exc

    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles).selectinload(UserRole.role))
    )
    user = result.scalar_one_or_none()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


async def get_user_permission_codes(user: User, db: AsyncSession) -> set[str]:
    if user.is_superuser:
        return {p.value for p in Perm}
    codes: set[str] = set()
    for ur in user.roles:
        codes.update(ROLE_PERMISSIONS.get(ur.role.name, []))
    role_ids = [ur.role_id for ur in user.roles]
    if role_ids:
        q = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id.in_(role_ids))
        )
        rows = await db.execute(q)
        codes.update(r[0] for r in rows.all())
    return codes


def require_permission(permission: str):
    async def _checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        codes = await get_user_permission_codes(user, db)
        if permission not in codes and Perm.ADMIN.value not in codes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return user

    return _checker


require_admin = require_permission(Perm.ADMIN.value)
require_approve = require_permission(Perm.CALCULATIONS_APPROVE.value)
