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

"""Внутренний API для ai_agent: активный провайдер."""

from fastapi import APIRouter, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.models.ai_provider import AiProvider, AiProviderSettings
from fastapi import Depends

router = APIRouter(prefix="/internal", tags=["internal"])


def _verify_internal_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != settings.ai_agent_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.get("/ai-provider")
async def get_active_provider(
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(_verify_internal_key),
) -> dict:
    settings_row = (await db.execute(select(AiProviderSettings).limit(1))).scalar_one_or_none()
    if settings_row and settings_row.active_provider_id:
        provider = await db.get(AiProvider, settings_row.active_provider_id)
        if provider and provider.is_active:
            return {
                "name": provider.name,
                "base_url": provider.base_url,
                "model_name": provider.model_name,
                "provider_type": provider.provider_type.value,
            }
    provider = (
        await db.execute(select(AiProvider).where(AiProvider.is_active.is_(True)).limit(1))
    ).scalar_one_or_none()
    if provider:
        return {
            "name": provider.name,
            "base_url": provider.base_url,
            "model_name": provider.model_name,
            "provider_type": provider.provider_type.value,
        }
    return {
        "name": "ollama-local",
        "base_url": "http://localhost:11434",
        "model_name": "qwen2.5-coder",
        "provider_type": "local",
    }
