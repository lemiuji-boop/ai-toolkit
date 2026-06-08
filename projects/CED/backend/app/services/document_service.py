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

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.path_security import resolve_allowed_path, safe_upload_filename
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion


async def get_document_or_404(db: AsyncSession, document_id: int) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None or doc.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


async def save_upload_file(file: UploadFile, doc_number: str, archive: bool = False) -> tuple[str, str]:
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл превышает лимит {settings.max_upload_bytes // (1024 * 1024)} МБ",
        )
    digest = hashlib.sha256(content).hexdigest()
    now = datetime.now(timezone.utc)
    prefix = doc_number[:3] if len(doc_number) >= 3 else doc_number
    subdir = Path(str(now.year)) / f"{now.month:02d}" / prefix
    if archive:
        subdir = Path("archive") / subdir

    storage_root = Path(settings.file_storage_root)
    final_dir = storage_root / subdir
    final_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_upload_filename(file.filename)
    path = final_dir / safe_name
    path.write_bytes(content)
    return str(path), digest


async def create_version(
    db: AsyncSession,
    document: Document,
    file_path: str,
    file_hash: str,
    version_index: str,
    uploaded_by: int | None = None,
    change_summary: str | None = None,
) -> DocumentVersion:
    version = DocumentVersion(
        document_id=document.id,
        version_index=version_index,
        file_path=file_path,
        file_hash=file_hash,
        uploaded_by=uploaded_by,
        change_summary=change_summary,
    )
    db.add(version)
    await db.flush()
    document.current_version_id = version.id
    document.updated_at = datetime.now(timezone.utc)
    return version


async def archive_document(document: Document) -> None:
    document.status = DocumentStatus.archived
