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

"""Документы и файлы расчёта."""
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Perm, require_permission
from app.db.models import Document, StoredFile, User
from app.db.session import get_db
from app.schemas.documents import DocumentResponse
from app.schemas.files import FileResponse

router = APIRouter(tags=["calculation-files"])


class CalculationDocumentsResponse(BaseModel):
    files: list[FileResponse]
    documents: list[DocumentResponse]


@router.get("/calculations/{calculation_id}/files", response_model=list[FileResponse])
async def list_calculation_files(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[StoredFile]:
    result = await db.execute(
        select(StoredFile)
        .where(StoredFile.calculation_id == calculation_id)
        .order_by(StoredFile.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/calculations/{calculation_id}/documents", response_model=list[DocumentResponse])
async def list_calculation_documents(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    files = (
        await db.execute(select(StoredFile.id).where(StoredFile.calculation_id == calculation_id))
    ).scalars().all()
    if not files:
        return []
    result = await db.execute(select(Document).where(Document.file_id.in_(files)))
    return list(result.scalars().all())
