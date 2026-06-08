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

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.services.auth_service import decode_access_token
from app.services.storage_access import StorageAccessMode, storage

security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    user_id = int(decode_access_token(credentials.credentials))
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(roles: list[UserRole]) -> Callable:
    async def _role_guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _role_guard


async def require_mutation_access(current_user: User = Depends(get_current_user)) -> User:
    """Мутации разрешены только admin/moderator при READ_WRITE на каталоге."""
    if current_user.role == UserRole.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Read-only role")
    if storage.check_access() != StorageAccessMode.READ_WRITE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Каталог доступен только для чтения",
        )
    return current_user
