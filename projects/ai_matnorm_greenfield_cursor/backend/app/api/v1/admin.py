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

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import write_audit
from app.core.encryption import encrypt_secret
from app.core.permissions import Perm, require_admin
from app.core.security import hash_password
from app.db.models import (
    AiProvider,
    AiRequest,
    AllowanceRule,
    ApiKeySecret,
    Job,
    KimRule,
    Material,
    SecurityEvent,
    Role,
    User,
    UserRole,
    UserStatus,
)
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def admin_ping(_user: User = Depends(require_admin)) -> dict[str, str]:
    return {"status": "admin_ok"}


class UserAdminResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    status: str

    model_config = {"from_attributes": True}


class UserAdminCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role_name: str = "technologist"


@router.post("/users", response_model=UserAdminResponse, status_code=201)
async def create_user(
    body: UserAdminCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email уже занят")
    role = (
        await db.execute(select(Role).where(Role.name == body.role_name))
    ).scalar_one_or_none()
    if not role:
        role = Role(id=uuid.uuid4(), name=body.role_name, description=body.role_name)
        db.add(role)
        await db.flush()
    user = User(
        id=uuid.uuid4(),
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id))
    await write_audit(
        db,
        user_id=admin.id,
        action="admin_create_user",
        entity_type="user",
        entity_id=str(user.id),
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/users", response_model=list[UserAdminResponse])
async def list_users(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())


class AiProviderCreate(BaseModel):
    name: str
    provider_type: str
    base_url: str | None = None
    api_key: str | None = None
    is_enabled: bool = True
    priority: int = 100


class AiProviderResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider_type: str
    base_url: str | None
    is_enabled: bool
    priority: int

    model_config = {"from_attributes": True}


@router.get("/ai-providers", response_model=list[AiProviderResponse])
async def list_ai_providers(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[AiProvider]:
    result = await db.execute(select(AiProvider).order_by(AiProvider.priority))
    return list(result.scalars().all())


class AiProviderUpdate(BaseModel):
    name: str | None = None
    provider_type: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    is_enabled: bool | None = None
    priority: int | None = None


@router.patch("/ai-providers/{provider_id}", response_model=AiProviderResponse)
async def update_ai_provider(
    provider_id: uuid.UUID,
    body: AiProviderUpdate,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AiProvider:
    result = await db.execute(select(AiProvider).where(AiProvider.id == provider_id))
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Провайдер не найден")
    for field in ("name", "provider_type", "base_url", "is_enabled", "priority"):
        val = getattr(body, field)
        if val is not None:
            setattr(provider, field, val)
    if body.api_key:
        secret = (
            await db.execute(
                select(ApiKeySecret).where(ApiKeySecret.provider_id == provider_id)
            )
        ).scalar_one_or_none()
        if secret:
            secret.encrypted_value = encrypt_secret(body.api_key)
        else:
            db.add(
                ApiKeySecret(
                    id=uuid.uuid4(),
                    provider_id=provider_id,
                    encrypted_value=encrypt_secret(body.api_key),
                )
            )
    await db.commit()
    await db.refresh(provider)
    return provider


@router.delete("/ai-providers/{provider_id}", status_code=204)
async def delete_ai_provider(
    provider_id: uuid.UUID,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(AiProvider).where(AiProvider.id == provider_id))
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(status_code=404, detail="Провайдер не найден")
    await db.delete(provider)
    await db.commit()


@router.post("/ai-providers/{provider_id}/test-connection")
async def test_ai_provider_connection(
    provider_id: uuid.UUID,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    from app.services.llm_router.factory import test_provider_connection

    return await test_provider_connection(db, provider_id)


@router.post("/ai-providers", response_model=AiProviderResponse, status_code=201)
async def create_ai_provider(
    body: AiProviderCreate,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AiProvider:
    provider = AiProvider(
        id=uuid.uuid4(),
        name=body.name,
        provider_type=body.provider_type,
        base_url=body.base_url,
        is_enabled=body.is_enabled,
        priority=body.priority,
    )
    db.add(provider)
    await db.flush()
    if body.api_key:
        db.add(
            ApiKeySecret(
                id=uuid.uuid4(),
                provider_id=provider.id,
                encrypted_value=encrypt_secret(body.api_key),
            )
        )
    await db.commit()
    await db.refresh(provider)
    return provider


@router.get("/token-usage")
async def token_usage(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    total_prompt = await db.execute(select(func.sum(AiRequest.prompt_tokens)))
    total_completion = await db.execute(select(func.sum(AiRequest.completion_tokens)))
    count = await db.execute(select(func.count(AiRequest.id)))
    return {
        "requests": count.scalar() or 0,
        "prompt_tokens": total_prompt.scalar() or 0,
        "completion_tokens": total_completion.scalar() or 0,
    }


@router.get("/jobs")
async def admin_jobs(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(select(Job).order_by(Job.created_at.desc()).limit(50))
    return [
        {"id": str(j.id), "status": j.status.value, "type": j.job_type, "progress": j.progress_percent}
        for j in result.scalars().all()
    ]


@router.get("/security-events")
async def security_events(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(100)
    )
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "user_id": str(e.user_id) if e.user_id else None,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]


@router.get("/materials-dictionary")
async def materials_dictionary(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    mats = (await db.execute(select(Material))).scalars().all()
    return [{"id": str(m.id), "code": m.code, "name": m.name} for m in mats]


@router.post("/seed-default-rules")
async def seed_default_rules(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    existing = (await db.execute(select(KimRule))).scalars().first()
    if not existing:
        db.add(
            KimRule(
                id=uuid.uuid4(),
                material_type="sheet_metal",
                process_type="cutting",
                kim_value=0.78,
                description="Листовой металл",
            )
        )
        db.add(
            AllowanceRule(
                id=uuid.uuid4(),
                material_type="sheet_metal",
                allowance_value=0.12,
                description="Припуск лист",
            )
        )
        db.add(
            Material(
                id=uuid.uuid4(),
                code="AMG6M",
                name="АМг6М",
                material_type="sheet_metal",
                unit="kg",
            )
        )
        await db.commit()
    return {"status": "ok"}
