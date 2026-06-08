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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db_session
from app.models.ai_provider import AiProvider, AiProviderSettings, AiProviderType
from app.models.user import User, UserRole
from app.services.crypto_service import encrypt_secret

router = APIRouter(prefix="/admin/ai-providers", tags=["ai-providers"])


@router.get("")
async def list_providers(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> list[dict]:
    rows = (await db.execute(select(AiProvider))).scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type.value,
            "base_url": p.base_url,
            "model_name": p.model_name,
            "is_active": p.is_active,
        }
        for p in rows
    ]


@router.post("")
async def create_provider(
    payload: dict,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict:
    settings_row = await _get_settings(db)
    provider_type = AiProviderType(payload.get("provider_type", "local"))
    if provider_type == AiProviderType.external and not settings_row.allow_external_providers:
        raise HTTPException(status_code=403, detail="Внешние провайдеры отключены")

    api_key = payload.get("api_key")
    encrypted = encrypt_secret(api_key) if api_key else None
    provider = AiProvider(
        provider_type=provider_type,
        name=payload["name"],
        base_url=payload["base_url"],
        api_key_encrypted=encrypted,
        model_name=payload.get("model_name"),
        is_active=payload.get("is_active", False),
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return {"id": provider.id}


@router.get("/settings")
async def get_settings(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict:
    row = await _get_settings(db)
    return {
        "allow_external_providers": row.allow_external_providers,
        "active_provider_id": row.active_provider_id,
    }


@router.put("/settings")
async def update_settings(
    payload: dict,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict:
    row = await _get_settings(db)
    row.allow_external_providers = bool(payload.get("allow_external_providers", row.allow_external_providers))
    row.active_provider_id = payload.get("active_provider_id", row.active_provider_id)
    await db.commit()
    return {"allow_external_providers": row.allow_external_providers, "active_provider_id": row.active_provider_id}


@router.put("/{provider_id}")
async def update_provider(
    provider_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict:
    provider = await db.get(AiProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if "name" in payload:
        provider.name = payload["name"]
    if "base_url" in payload:
        provider.base_url = payload["base_url"]
    if "model_name" in payload:
        provider.model_name = payload["model_name"]
    if "is_active" in payload:
        provider.is_active = bool(payload["is_active"])
    if payload.get("api_key"):
        provider.api_key_encrypted = encrypt_secret(payload["api_key"])
    await db.commit()
    return {"id": provider.id}


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin])),
) -> dict[str, str]:
    provider = await db.get(AiProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    await db.delete(provider)
    await db.commit()
    return {"status": "deleted"}


async def _get_settings(db: AsyncSession) -> AiProviderSettings:
    row = (await db.execute(select(AiProviderSettings).limit(1))).scalar_one_or_none()
    if row is None:
        row = AiProviderSettings(allow_external_providers=False)
        db.add(row)
        await db.flush()
    return row
