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

"""Инициализация данных при старте приложения."""

import logging
import os

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.ai_provider import AiProvider, AiProviderSettings, AiProviderType
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def ensure_defaults() -> None:
    async with AsyncSessionLocal() as db:
        admin = (
            await db.execute(select(User).where(User.login == "admin"))
        ).scalar_one_or_none()
        if admin is None:
            db.add(
                User(
                    login="admin",
                    password_hash=get_password_hash("admin"),
                    role=UserRole.admin,
                    full_name="Администратор",
                    is_active=True,
                    must_change_password=True,
                )
            )
            logger.info("Создан пользователь admin/admin")

        settings = (await db.execute(select(AiProviderSettings).limit(1))).scalar_one_or_none()
        if settings is None:
            db.add(AiProviderSettings(allow_external_providers=False, active_provider_id=None))

        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        provider = (await db.execute(select(AiProvider).limit(1))).scalar_one_or_none()
        if provider is None:
            db.add(
                AiProvider(
                    provider_type=AiProviderType.local,
                    name="Ollama Local",
                    base_url=ollama_url,
                    model_name="qwen2.5-coder",
                    is_active=True,
                )
            )
        await db.commit()
