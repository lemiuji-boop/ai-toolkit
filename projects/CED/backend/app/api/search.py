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

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentOut

router = APIRouter()


@router.get("/search", response_model=DocumentListResponse)
async def search_documents(
    q: str = Query(default=""),
    status: str | None = Query(default=None),
    type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> DocumentListResponse:
    filters = []
    if status:
        filters.append(Document.status == status)
    if type:
        filters.append(Document.doc_type == type)
    if department:
        filters.append(Document.department == department)
    if date_from:
        filters.append(Document.created_at >= date_from)
    if date_to:
        filters.append(Document.created_at <= date_to)

    base = select(Document)
    count = select(func.count(Document.id))

    if q.strip():
        ts_query = func.plainto_tsquery("russian", q)
        vector = func.to_tsvector("russian", Document.doc_number + text("' '") + Document.name)
        fts_filter = vector.op("@@")(ts_query)
        fallback = or_(Document.doc_number.ilike(f"%{q}%"), Document.name.ilike(f"%{q}%"))
        filters.append(or_(fts_filter, fallback))

    if filters:
        condition = and_(*filters)
        base = base.where(condition)
        count = count.where(condition)

    base = base.order_by(Document.updated_at.desc()).offset((page - 1) * size).limit(size)
    rows = (await db.execute(base)).scalars().all()
    total = (await db.execute(count)).scalar_one()

    return DocumentListResponse(items=[DocumentOut.model_validate(row, from_attributes=True) for row in rows], total_count=total)
