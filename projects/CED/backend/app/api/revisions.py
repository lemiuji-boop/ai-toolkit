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

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.record_revision import RecordRevision, RevisionTargetType
from app.models.user import User
from app.schemas.catalog import RevisionOut

router = APIRouter(tags=["revisions"])


@router.get("/records/{target_type}/{target_id}/history", response_model=list[RevisionOut])
async def record_history(
    target_type: str,
    target_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[RevisionOut]:
    try:
        ttype = RevisionTargetType(target_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid target_type") from exc

    stmt = (
        select(RecordRevision)
        .where(RecordRevision.target_type == ttype, RecordRevision.target_id == target_id)
        .order_by(RecordRevision.timestamp.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [RevisionOut.model_validate(row, from_attributes=True) for row in rows]
