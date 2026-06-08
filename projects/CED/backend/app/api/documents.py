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

from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_mutation_access
from app.core.config import settings
from app.core.database import get_db_session
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion
from app.models.record_revision import RevisionAction, RevisionTargetType
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentListResponse, DocumentOut, DocumentUpdate, VersionOut
from app.core.path_security import resolve_allowed_path
from app.services.document_service import archive_document, create_version, get_document_or_404, save_upload_file
from app.services.log_service import write_log
from app.services.revision_service import record_revision
from app.services.soft_delete_service import soft_delete_document
from app.tasks.document_tasks import analyze_document

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> DocumentListResponse:
    query = select(Document).where(Document.deleted_at.is_(None))
    count_query = select(func.count(Document.id)).where(Document.deleted_at.is_(None))

    if status_filter:
        query = query.where(Document.status == status_filter)
        count_query = count_query.where(Document.status == status_filter)

    query = query.order_by(desc(Document.updated_at)).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    items = result.scalars().all()
    total = (await db.execute(count_query)).scalar_one()

    return DocumentListResponse(items=[DocumentOut.model_validate(i, from_attributes=True) for i in items], total_count=total)


@router.post("", response_model=DocumentOut)
async def create_document(
    payload: DocumentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> DocumentOut:
    document = Document(
        doc_number=payload.doc_number,
        name=payload.name,
        doc_type=payload.doc_type,
        status=DocumentStatus.active,
        department=payload.department,
        created_by=current_user.id,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(document)
    await db.flush()
    await write_log(
        db,
        "document.create",
        "document",
        str(document.id),
        current_user.id,
        payload.model_dump(),
        request.client.host if request.client else None,
    )
    await record_revision(
        db,
        target_type=RevisionTargetType.document,
        target_id=document.id,
        action=RevisionAction.create,
        changed_fields=payload.model_dump(),
        user=current_user,
    )
    await db.commit()
    await db.refresh(document)
    return DocumentOut.model_validate(document, from_attributes=True)


@router.post("/upload", response_model=DocumentOut)
async def create_document_with_file(
    request: Request,
    doc_number: str = Form(...),
    name: str = Form(...),
    doc_type: str = Form(...),
    version_index: str = Form(default="А"),
    department: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> DocumentOut:
    """Создание документа с PDF в одном запросе (CURSOR_LAUNCH)."""
    document = Document(
        doc_number=doc_number,
        name=name,
        doc_type=doc_type,
        status=DocumentStatus.active,
        department=department,
        created_by=current_user.id,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(document)
    await db.flush()

    file_path, file_hash = await save_upload_file(file, doc_number)
    version = await create_version(db, document, file_path, file_hash, version_index, current_user.id, "Первичная загрузка")
    document.source_file_hash = file_hash
    document.ocr_processed = False

    fields = {"doc_number": doc_number, "name": name, "doc_type": doc_type, "version_index": version_index}
    await write_log(db, "document.create", "document", str(document.id), current_user.id, fields, request.client.host if request.client else None)
    await record_revision(db, target_type=RevisionTargetType.document, target_id=document.id, action=RevisionAction.create, changed_fields=fields, user=current_user)
    await db.commit()
    analyze_document.delay(version.file_path, version.id)
    await db.refresh(document)
    return DocumentOut.model_validate(document, from_attributes=True)


@router.post("/upload-batch")
async def upload_batch(
    request: Request,
    files: list[UploadFile] = File(...),
    doc_type: str = Form(default="drawing"),
    version_index: str = Form(default="А"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> dict:
    """Пакетная загрузка PDF: имя файла → обозначение (без .pdf)."""
    results: list[dict] = []
    for file in files:
        stem = (file.filename or "doc").rsplit(".", 1)[0]
        try:
            document = Document(
                doc_number=stem[:128],
                name=stem[:512],
                doc_type=doc_type,
                status=DocumentStatus.active,
                created_by=current_user.id,
                updated_at=datetime.now(timezone.utc),
            )
            db.add(document)
            await db.flush()
            file_path, file_hash = await save_upload_file(file, document.doc_number)
            version = await create_version(
                db, document, file_path, file_hash, version_index, current_user.id, "Пакетная загрузка"
            )
            document.source_file_hash = file_hash
            document.ocr_processed = False
            results.append(
                {
                    "file": file.filename,
                    "status": "ok",
                    "document_id": document.id,
                    "version_id": version.id,
                    "file_path": file_path,
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append({"file": file.filename, "status": "error", "error": str(exc)})
    await db.commit()
    for row in results:
        if row.get("status") == "ok":
            analyze_document.delay(row["file_path"], row["version_id"])
    return {"total": len(files), "results": results}


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: int, db: AsyncSession = Depends(get_db_session), _: User = Depends(get_current_user)
) -> DocumentOut:
    document = await get_document_or_404(db, document_id)
    return DocumentOut.model_validate(document, from_attributes=True)


@router.put("/{document_id}", response_model=DocumentOut)
async def update_document(
    document_id: int,
    payload: DocumentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> DocumentOut:
    document = await get_document_or_404(db, document_id)
    updates = payload.model_dump(exclude_none=True)
    changed_fields: dict = {}
    for field, value in updates.items():
        old = getattr(document, field)
        old_val = old.value if hasattr(old, "value") else old
        changed_fields[field] = {"old": old_val, "new": value}
        setattr(document, field, value)
    document.updated_at = datetime.now(timezone.utc)
    await write_log(
        db,
        "document.update",
        "document",
        str(document.id),
        current_user.id,
        updates,
        request.client.host if request.client else None,
    )
    await record_revision(
        db,
        target_type=RevisionTargetType.document,
        target_id=document.id,
        action=RevisionAction.update,
        changed_fields=changed_fields,
        user=current_user,
    )
    await db.commit()
    await db.refresh(document)
    return DocumentOut.model_validate(document, from_attributes=True)


@router.get("/{document_id}/versions", response_model=list[VersionOut])
async def list_versions(
    document_id: int, db: AsyncSession = Depends(get_db_session), _: User = Depends(get_current_user)
) -> list[VersionOut]:
    await get_document_or_404(db, document_id)
    result = await db.execute(
        select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(desc(DocumentVersion.id))
    )
    return [VersionOut.model_validate(v, from_attributes=True) for v in result.scalars().all()]


@router.post("/{document_id}/versions", response_model=VersionOut)
async def upload_version(
    document_id: int,
    request: Request,
    version_index: str = Query(..., min_length=1),
    change_summary: str | None = Query(default=None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> VersionOut:
    document = await get_document_or_404(db, document_id)

    if document.current_version_id:
        await archive_document(document)

    file_path, file_hash = await save_upload_file(file, document.doc_number, archive=True)
    version = await create_version(db, document, file_path, file_hash, version_index, current_user.id, change_summary)
    document.status = DocumentStatus.active
    document.source_file_hash = file_hash

    await write_log(
        db,
        "document.version.upload",
        "document_version",
        str(version.id),
        current_user.id,
        {"document_id": document_id, "version_index": version_index},
        request.client.host if request and request.client else None,
    )
    await record_revision(
        db,
        target_type=RevisionTargetType.document,
        target_id=document.id,
        action=RevisionAction.update,
        changed_fields={"version_index": version_index, "file_hash": file_hash},
        user=current_user,
    )
    await db.commit()
    analyze_document.delay(version.file_path, version.id)
    await db.refresh(version)
    return VersionOut.model_validate(version, from_attributes=True)


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> dict[str, str]:
    document = await get_document_or_404(db, document_id)
    await soft_delete_document(db, document, current_user)
    await write_log(db, "document.delete", "document", str(document.id), current_user.id, {})
    await db.commit()
    return {"status": "deleted"}


@router.get("/{document_id}/file")
async def download_current_file(
    document_id: int, db: AsyncSession = Depends(get_db_session), _: User = Depends(get_current_user)
) -> FileResponse:
    document = await get_document_or_404(db, document_id)
    if not document.current_version_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current version not found")

    result = await db.execute(select(DocumentVersion).where(DocumentVersion.id == document.current_version_id))
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    safe_path = resolve_allowed_path(version.file_path)
    return FileResponse(path=str(safe_path), filename=safe_path.name)
