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

"""CLI команды: seed администратора, миграции."""
import asyncio
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import Permission, Role, RolePermission, User, UserRole, UserStatus
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.core.permissions import ROLE_PERMISSIONS, Perm


async def seed_admin() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Роли
        role_defs = [
            ("administrator", "Администратор"),
            ("technologist", "Технолог"),
            ("senior_technologist", "Старший технолог"),
            ("guest", "Гость"),
        ]
        roles: dict[str, Role] = {}
        for name, desc in role_defs:
            r = await db.execute(select(Role).where(Role.name == name))
            role = r.scalar_one_or_none()
            if not role:
                role = Role(id=uuid.uuid4(), name=name, description=desc)
                db.add(role)
            roles[name] = role

        # Permissions
        for perm in Perm:
            p = await db.execute(select(Permission).where(Permission.code == perm.value))
            if not p.scalar_one_or_none():
                db.add(Permission(id=uuid.uuid4(), code=perm.value, description=perm.name))

        await db.flush()

        for role_name, codes in ROLE_PERMISSIONS.items():
            role = roles[role_name]
            for code in codes:
                perm_r = await db.execute(select(Permission).where(Permission.code == code))
                perm = perm_r.scalar_one()
                exists = await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id,
                    )
                )
                if not exists.scalar_one_or_none():
                    db.add(
                        RolePermission(
                            id=uuid.uuid4(),
                            role_id=role.id,
                            permission_id=perm.id,
                        )
                    )

        # Admin user
        u = await db.execute(select(User).where(User.email == settings.admin_email))
        user = u.scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=settings.admin_email,
                full_name="Администратор",
                password_hash=hash_password(settings.admin_password),
                is_superuser=True,
                status=UserStatus.ACTIVE,
            )
            db.add(user)
            await db.flush()
            db.add(
                UserRole(id=uuid.uuid4(), user_id=user.id, role_id=roles["administrator"].id)
            )
            print(f"Создан администратор: {settings.admin_email}")
        else:
            # seed_admin: пароль всегда берём из ADMIN_PASSWORD в .env
            user.password_hash = hash_password(settings.admin_password)
            print(f"Пароль администратора синхронизирован с .env: {settings.admin_email}")

        await db.commit()


def main() -> None:
    import sys

    if len(sys.argv) < 2 or sys.argv[1] != "seed_admin":
        print("Использование: python -m app.cli seed_admin")
        return
    asyncio.run(seed_admin())


if __name__ == "__main__":
    main()
