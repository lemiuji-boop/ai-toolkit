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

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.change_order import ChangeOrder
from app.models.change_order_directive import ChangeOrderDirective
from app.models.document import Document
from app.models.user import User
from app.schemas.catalog import ChangeOrderOut, DirectiveOut

router = APIRouter()


@router.get("/documents/{document_id}/change-orders", response_model=list[ChangeOrderOut])
async def change_orders_for_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[ChangeOrderOut]:
    doc = await db.get(Document, document_id)
    if not doc or doc.deleted_at:
        raise HTTPException(status_code=404, detail="Document not found")

    stmt = (
        select(ChangeOrder)
        .join(ChangeOrderDirective, ChangeOrderDirective.change_order_id == ChangeOrder.id)
        .where(
            (ChangeOrderDirective.document_id == document_id)
            | (ChangeOrderDirective.affected_doc_number == doc.doc_number)
        )
        .where(ChangeOrder.deleted_at.is_(None))
        .options(selectinload(ChangeOrder.directives))
        .distinct()
    )
    result = await db.execute(stmt)
    return [ChangeOrderOut.model_validate(row, from_attributes=True) for row in result.scalars().all()]


@router.get("/change-orders/{order_id}/documents", response_model=list[dict])
async def documents_for_change_order(
    order_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[dict]:
    order = await db.get(ChangeOrder, order_id)
    if not order or order.deleted_at:
        raise HTTPException(status_code=404, detail="Change order not found")

    directives = (
        await db.execute(select(ChangeOrderDirective).where(ChangeOrderDirective.change_order_id == order_id))
    ).scalars().all()

    doc_ids = [d.document_id for d in directives if d.document_id]
    doc_numbers = [d.affected_doc_number for d in directives if d.affected_doc_number]

    stmt = select(Document).where(Document.deleted_at.is_(None)).where(
        (Document.id.in_(doc_ids)) | (Document.doc_number.in_(doc_numbers))
    )
    docs = (await db.execute(stmt)).scalars().all()
    return [{"id": d.id, "doc_number": d.doc_number, "name": d.name} for d in docs]


@router.get("/change-orders", response_model=list[ChangeOrderOut])
async def list_change_orders(
    backlog: str | None = None,
    impl_from: date | None = Query(default=None, alias="impl_from"),
    impl_to: date | None = Query(default=None, alias="impl_to"),
    product: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[ChangeOrderOut]:
    stmt = select(ChangeOrder).where(ChangeOrder.deleted_at.is_(None)).options(selectinload(ChangeOrder.directives))
    if backlog or impl_from or impl_to or product:
        stmt = stmt.join(ChangeOrderDirective)
        if backlog:
            stmt = stmt.where(ChangeOrderDirective.backlog_action == backlog)
        if impl_from:
            stmt = stmt.where(ChangeOrderDirective.implementation_date >= impl_from)
        if impl_to:
            stmt = stmt.where(ChangeOrderDirective.implementation_date <= impl_to)
        if product:
            stmt = stmt.where(ChangeOrderDirective.implementation_product.ilike(f"%{product}%"))

    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    return [ChangeOrderOut.model_validate(row, from_attributes=True) for row in result.scalars().unique().all()]
