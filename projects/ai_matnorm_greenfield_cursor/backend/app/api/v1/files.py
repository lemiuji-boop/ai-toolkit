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

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.permissions import Perm, get_current_user, require_permission
from app.core.revision_guard import assert_calculation_editable
from app.db.models import StoredFile, User
from app.db.session import get_db
from app.schemas.files import FileDownloadResponse, FileResponse
from app.services.file_ingestion.validator import safe_extract_zip, validate_upload
from app.services.storage.s3 import get_storage

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=list[FileResponse])
async def upload_files(
    files: list[UploadFile] = File(...),
    calculation_id: uuid.UUID | None = Form(None),
    user: User = Depends(require_permission(Perm.FILES_UPLOAD.value)),
    db: AsyncSession = Depends(get_db),
) -> list[StoredFile]:
    if calculation_id:
        await assert_calculation_editable(db, calculation_id)
    storage = get_storage()
    saved: list[StoredFile] = []

    async def _save_one(name: str, data: bytes, mime: str) -> StoredFile:
        validate_upload(name, mime, len(data), settings.max_upload_size_mb)
        key, sha = storage.upload_bytes(
            data, bucket=settings.s3_bucket_quarantine, content_type=mime
        )
        sf = StoredFile(
            id=uuid.uuid4(),
            calculation_id=calculation_id,
            original_name=name,
            mime_type=mime,
            size_bytes=len(data),
            storage_key=key,
            sha256=sha,
            is_quarantined=True,
            uploaded_by_id=user.id,
        )
        db.add(sf)
        saved.append(sf)
        return sf

    for upload in files:
        data = await upload.read()
        name = upload.filename or "unnamed"
        mime = upload.content_type or "application/octet-stream"
        if name.lower().endswith(".zip"):
            for inner_name, inner_data in safe_extract_zip(data):
                await _save_one(inner_name, inner_data, mime)
        else:
            await _save_one(name, data, mime)

    await db.commit()
    for sf in saved:
        await db.refresh(sf)
    return saved


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StoredFile:
    sf = await db.get(StoredFile, file_id)
    if not sf:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return sf


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileDownloadResponse:
    sf = await db.get(StoredFile, file_id)
    if not sf:
        raise HTTPException(status_code=404, detail="Файл не найден")
    bucket = settings.s3_bucket_quarantine if sf.is_quarantined else settings.s3_bucket
    url = get_storage().presigned_url(sf.storage_key, bucket=bucket)
    return FileDownloadResponse(download_url=url)
