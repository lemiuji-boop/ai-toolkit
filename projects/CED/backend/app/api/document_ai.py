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

"""Прокси к ИИ-агенту для операций с документом."""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db_session
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.core.path_security import resolve_allowed_path
from app.services.document_service import get_document_or_404

router = APIRouter(tags=["document-ai"])


async def _get_file_path(db: AsyncSession, document_id: int) -> str:
    document = await get_document_or_404(db, document_id)
    if not document.current_version_id:
        raise HTTPException(status_code=404, detail="Версия файла не найдена")
    version = await db.get(DocumentVersion, document.current_version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Версия не найдена")
    return str(resolve_allowed_path(version.file_path))


@router.post("/{document_id}/analyze")
async def analyze_document_now(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict:
    file_path = await _get_file_path(db, document_id)
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ai_agent_base_url}/analyze",
            json={"file_path": file_path, "doc_kind": "kd"},
            headers={"X-API-Key": settings.ai_agent_api_key},
        )
        response.raise_for_status()
        return response.json()


@router.post("/{document_id}/validate")
async def validate_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict:
    document = await get_document_or_404(db, document_id)
    file_path = await _get_file_path(db, document_id)
    async with httpx.AsyncClient(timeout=60.0) as client:
        analyze_resp = await client.post(
            f"{settings.ai_agent_base_url}/analyze",
            json={"file_path": file_path, "doc_kind": "kd"},
            headers={"X-API-Key": settings.ai_agent_api_key},
        )
        analyze_resp.raise_for_status()
        extracted = analyze_resp.json().get("data", {})
        validate_resp = await client.post(
            f"{settings.ai_agent_base_url}/validate",
            json={
                "extracted": extracted,
                "expected": {"doc_number": document.doc_number, "name": document.name},
            },
            headers={"X-API-Key": settings.ai_agent_api_key},
        )
        validate_resp.raise_for_status()
        return validate_resp.json()
