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

"""Мягкое удаление с переносом файлов в _ARCHIVE."""

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.record_revision import RevisionAction, RevisionTargetType
from app.models.user import User
from app.services.revision_service import record_revision
from app.services.storage_access import storage


async def soft_delete_document(db: AsyncSession, document: Document, user: User | None) -> None:
    document.deleted_at = datetime.now(timezone.utc)
    if document.current_version_id:
        version = await db.get(DocumentVersion, document.current_version_id)
        if version and version.file_path:
            src = Path(version.file_path)
            if src.exists():
                rel = document.catalog_path or document.doc_number
                dst_dir = storage.archive_path() / rel
                storage.mkdir(dst_dir)
                storage.move_file(src, dst_dir / src.name)
    await record_revision(
        db,
        target_type=RevisionTargetType.document,
        target_id=document.id,
        action=RevisionAction.delete,
        changed_fields={"deleted_at": {"old": None, "new": document.deleted_at.isoformat()}},
        user=user,
    )
