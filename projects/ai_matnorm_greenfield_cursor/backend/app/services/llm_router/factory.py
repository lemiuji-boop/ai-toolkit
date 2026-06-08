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

"""Сборка LLM router из записей AiProvider в БД."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.encryption import decrypt_secret
from app.db.models import AiModel, AiProvider, ApiKeySecret
from app.services.llm_router.router import (
    LlmProvider,
    LlmRouter,
    MockLlmProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
)


async def _load_api_key(db: AsyncSession, provider_id: uuid.UUID) -> str | None:
    result = await db.execute(
        select(ApiKeySecret).where(ApiKeySecret.provider_id == provider_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    return decrypt_secret(row.encrypted_value)


async def _default_model(db: AsyncSession, provider_id: uuid.UUID) -> str:
    result = await db.execute(
        select(AiModel)
        .where(AiModel.provider_id == provider_id)
        .order_by(AiModel.is_default.desc())
    )
    model = result.scalars().first()
    if model:
        return model.model_name
    return "llama3.2"


def _provider_instance(
    row: AiProvider,
    api_key: str | None,
    model_name: str,
) -> LlmProvider | None:
    if row.provider_type == "ollama":
        base = row.base_url or settings.ollama_base_url
        return OllamaProvider(base, model=model_name)
    if row.provider_type in ("openai", "openai_compatible", "external"):
        if not row.base_url or not api_key:
            return None
        return OpenAICompatibleProvider(row.base_url, api_key, model_name)
    if row.provider_type == "mock":
        return MockLlmProvider()
    return None


class DbBackedProvider:
    """Обёртка: хранит id провайдера для журнала ai_requests."""

    def __init__(self, provider_id: uuid.UUID, inner: LlmProvider) -> None:
        self.provider_id = provider_id
        self.inner = inner

    async def chat(self, request):  # type: ignore[no-untyped-def]
        return await self.inner.chat(request)


async def build_router_from_db(db: AsyncSession) -> LlmRouter:
    """Активные провайдеры по priority; в конце mock fallback."""
    result = await db.execute(
        select(AiProvider)
        .where(AiProvider.is_enabled.is_(True))
        .order_by(AiProvider.priority)
    )
    rows = list(result.scalars().all())
    chain: list[LlmProvider] = []
    for row in rows:
        if not settings.external_llm_allowed and row.provider_type in (
            "openai",
            "openai_compatible",
            "external",
        ):
            continue
        api_key = await _load_api_key(db, row.id)
        model = await _default_model(db, row.id)
        inst = _provider_instance(row, api_key, model)
        if inst:
            chain.append(DbBackedProvider(row.id, inst))
    if not chain:
        chain.append(OllamaProvider(settings.ollama_base_url))
    chain.append(MockLlmProvider())
    return LlmRouter(chain)


async def test_provider_connection(db: AsyncSession, provider_id: uuid.UUID) -> dict[str, str]:
    """Проверка соединения с провайдером (FR-071)."""
    result = await db.execute(select(AiProvider).where(AiProvider.id == provider_id))
    row = result.scalar_one_or_none()
    if not row:
        return {"status": "error", "detail": "Провайдер не найден"}
    api_key = await _load_api_key(db, row.id)
    model = await _default_model(db, row.id)
    inst = _provider_instance(row, api_key, model)
    if not inst:
        return {"status": "error", "detail": "Неполная конфигурация (base_url или api_key)"}
    from app.services.llm_router.router import LlmRequest

    try:
        await inst.chat(LlmRequest(task_type="ping", prompt='{"ok":true}'))
        return {"status": "valid", "detail": "Соединение успешно"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)[:500]}
