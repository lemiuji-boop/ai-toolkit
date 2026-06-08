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

"""Связывание документов по обозначениям и спецификациям."""
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AssemblyLink, Document, ExtractedFact, SpecRow, StoredFile


def _normalize_des(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().upper())


async def link_documents_for_calculation(
    db: AsyncSession, calculation_id: uuid.UUID
) -> list[AssemblyLink]:
    """Построение связей parent-child из фактов и строк спецификации."""
    existing = (
        await db.execute(select(AssemblyLink).where(AssemblyLink.calculation_id == calculation_id))
    ).scalars().all()
    for link in existing:
        await db.delete(link)

    file_ids = (
        await db.execute(
            select(StoredFile.id).where(StoredFile.calculation_id == calculation_id)
        )
    ).scalars().all()
    if not file_ids:
        return []

    docs = (
        await db.execute(select(Document).where(Document.file_id.in_(file_ids)))
    ).scalars().all()

    designations: dict[str, uuid.UUID] = {}
    for doc in docs:
        facts = (
            await db.execute(
                select(ExtractedFact).where(
                    ExtractedFact.document_id == doc.id,
                    ExtractedFact.field == "designation",
                )
            )
        ).scalars().all()
        for f in facts:
            if f.value:
                designations[_normalize_des(f.value)] = doc.id

    links: list[AssemblyLink] = []
    root_des = next(iter(designations.keys()), "ROOT")

    for doc in docs:
        if doc.document_type != "specification":
            continue
        rows = (
            await db.execute(select(SpecRow).where(SpecRow.document_id == doc.id))
        ).scalars().all()
        for row in rows:
            if not row.designation:
                continue
            child = _normalize_des(row.designation)
            link = AssemblyLink(
                id=uuid.uuid4(),
                calculation_id=calculation_id,
                parent_designation=root_des,
                child_designation=child,
                quantity=row.quantity or 1.0,
                confidence=row.confidence,
                source_document_id=doc.id,
            )
            db.add(link)
            links.append(link)

    # Связи из фактов parent_designation если есть
    for doc in docs:
        facts = (
            await db.execute(select(ExtractedFact).where(ExtractedFact.document_id == doc.id))
        ).scalars().all()
        child_des = next((f.value for f in facts if f.field == "designation"), None)
        parent_des = next((f.value for f in facts if f.field == "parent_designation"), root_des)
        if child_des and parent_des:
            link = AssemblyLink(
                id=uuid.uuid4(),
                calculation_id=calculation_id,
                parent_designation=_normalize_des(parent_des),
                child_designation=_normalize_des(child_des),
                quantity=1.0,
                confidence=0.75,
                source_document_id=doc.id,
            )
            db.add(link)
            links.append(link)

    await db.flush()
    return links
