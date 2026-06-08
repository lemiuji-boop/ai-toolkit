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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, ExtractedFact, KsiNode, StoredFile
from app.services.assembly_linker import link_documents_for_calculation


def _propagate_quantities(nodes: list[KsiNode]) -> None:
    by_id = {n.id: n for n in nodes}
    for node in sorted(nodes, key=lambda n: n.level, reverse=True):
        if node.parent_id and node.parent_id in by_id:
            parent = by_id[node.parent_id]
            node.quantity_total = round(parent.quantity_total * node.quantity_per_parent, 4)


async def build_ksi_from_calculation(db: AsyncSession, calculation_id: uuid.UUID) -> list[KsiNode]:
    """Построение КСИ: assembly links → дерево узлов."""
    links = await link_documents_for_calculation(db, calculation_id)

    existing = (
        await db.execute(select(KsiNode).where(KsiNode.calculation_id == calculation_id))
    ).scalars().all()
    for n in existing:
        await db.delete(n)

    nodes: list[KsiNode] = []
    root_id = uuid.uuid4()
    root = KsiNode(
        id=root_id,
        calculation_id=calculation_id,
        parent_id=None,
        level=0,
        designation="ROOT",
        name="Сборочная единица",
        node_type="assembly",
        quantity_per_parent=1,
        quantity_total=1,
        confidence=0.95,
    )
    db.add(root)
    nodes.append(root)

    des_to_node: dict[str, uuid.UUID] = {"ROOT": root_id}

    for link in links:
        parent_id = des_to_node.get(link.parent_designation, root_id)
        child_key = link.child_designation
        if child_key in des_to_node:
            continue
        name = link.child_designation
        if link.source_document_id:
            facts = (
                await db.execute(
                    select(ExtractedFact).where(
                        ExtractedFact.document_id == link.source_document_id,
                        ExtractedFact.field == "name",
                    )
                )
            ).scalars().all()
            if facts:
                name = facts[0].value

        node = KsiNode(
            id=uuid.uuid4(),
            calculation_id=calculation_id,
            parent_id=parent_id,
            level=1,
            designation=link.child_designation[:128],
            name=name[:512],
            node_type="detail",
            quantity_per_parent=link.quantity,
            quantity_total=link.quantity,
            source_document_id=link.source_document_id,
            confidence=link.confidence,
        )
        db.add(node)
        nodes.append(node)
        des_to_node[child_key] = node.id

    # Документы без связей
    files = (
        await db.execute(select(StoredFile).where(StoredFile.calculation_id == calculation_id))
    ).scalars().all()
    for sf in files:
        docs = (
            await db.execute(select(Document).where(Document.file_id == sf.id))
        ).scalars().all()
        for doc in docs:
            facts = (
                await db.execute(select(ExtractedFact).where(ExtractedFact.document_id == doc.id))
            ).scalars().all()
            des = next((f.value for f in facts if f.field == "designation"), sf.original_name)
            key = des[:128]
            if key in des_to_node:
                continue
            name = next((f.value for f in facts if f.field == "name"), sf.original_name)
            node = KsiNode(
                id=uuid.uuid4(),
                calculation_id=calculation_id,
                parent_id=root_id,
                level=1,
                designation=key,
                name=name[:512],
                node_type="detail",
                quantity_per_parent=1,
                quantity_total=1,
                source_document_id=doc.id,
                confidence=0.8,
            )
            db.add(node)
            nodes.append(node)
            des_to_node[key] = node.id

    _propagate_quantities(nodes)
    await db.flush()
    return nodes
