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

"""Запросы универсального каталога и фильтров КД↔ИИ."""

from datetime import date

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.change_order import ChangeOrder
from app.models.change_order_directive import ChangeOrderDirective
from app.models.document import Document


def build_catalog_query(
    *,
    doc_number: str | None = None,
    name: str | None = None,
    order_number: str | None = None,
    backlog: str | None = None,
    impl_date_from: date | None = None,
    impl_date_to: date | None = None,
    product: str | None = None,
    status: str | None = None,
) -> Select:
    stmt = select(Document).where(Document.deleted_at.is_(None))

    if doc_number:
        stmt = stmt.where(Document.doc_number.ilike(f"%{doc_number}%"))
    if name:
        stmt = stmt.where(Document.name.ilike(f"%{name}%"))
    if product:
        stmt = stmt.where(Document.product_number.ilike(f"%{product}%"))
    if status:
        stmt = stmt.where(Document.status == status)

    if order_number or backlog or impl_date_from or impl_date_to:
        directive_filters = [ChangeOrder.deleted_at.is_(None)]
        if order_number:
            directive_filters.append(ChangeOrder.order_number.ilike(f"%{order_number}%"))
        if backlog:
            directive_filters.append(ChangeOrderDirective.backlog_action == backlog)
        if impl_date_from:
            directive_filters.append(ChangeOrderDirective.implementation_date >= impl_date_from)
        if impl_date_to:
            directive_filters.append(ChangeOrderDirective.implementation_date <= impl_date_to)

        doc_ids_subq = (
            select(ChangeOrderDirective.document_id)
            .join(ChangeOrder, ChangeOrder.id == ChangeOrderDirective.change_order_id)
            .where(and_(*directive_filters))
            .where(ChangeOrderDirective.document_id.is_not(None))
            .distinct()
        )
        affected_subq = (
            select(ChangeOrderDirective.affected_doc_number)
            .join(ChangeOrder, ChangeOrder.id == ChangeOrderDirective.change_order_id)
            .where(and_(*directive_filters))
            .where(ChangeOrderDirective.affected_doc_number.is_not(None))
            .distinct()
        )
        stmt = stmt.where(
            (Document.id.in_(doc_ids_subq)) | (Document.doc_number.in_(affected_subq))
        )

    return stmt.order_by(Document.catalog_path.nulls_last(), Document.doc_number)


async def paginate_catalog(
    db: AsyncSession,
    stmt: Select,
    page: int,
    size: int,
) -> tuple[list[Document], int]:
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = (await db.execute(count_stmt)).scalar_one()
    rows = (await db.execute(stmt.offset((page - 1) * size).limit(size))).scalars().all()
    return list(rows), total
