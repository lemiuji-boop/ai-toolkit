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

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_mutation_access
from app.core.database import get_db_session
from app.models.inbox_pending import InboxPending
from app.models.user import User, UserRole
from app.core.path_security import resolve_allowed_path
from app.services.inbox_service import ingest_file
from app.services.storage_access import storage
from app.tasks.inbox_tasks import ingest_file_task, scan_inbox_task

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/pending")
async def list_pending(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[dict]:
    rows = (await db.execute(select(InboxPending).order_by(InboxPending.created_at.desc()))).scalars().all()
    return [
        {
            "id": row.id,
            "file_path": row.file_path,
            "status": row.status,
            "reason": row.reason,
            "confidence": row.confidence,
        }
        for row in rows
    ]


@router.post("/process")
async def process_inbox(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_mutation_access),
) -> dict:
    if current_user.role not in (UserRole.admin, UserRole.moderator):
        return {"status": "forbidden"}
    scan_inbox_task.delay()
    return {"status": "queued"}


@router.post("/process-file")
async def process_single_file(
    file_path: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_mutation_access),
) -> dict:
    safe = str(resolve_allowed_path(file_path))
    result = await ingest_file(db, safe, storage)
    await db.commit()
    return result


@router.post("/process-file-async")
async def process_single_file_async(
    file_path: str,
    _: User = Depends(require_mutation_access),
) -> dict:
    task = ingest_file_task.delay(file_path)
    return {"task_id": task.id}
