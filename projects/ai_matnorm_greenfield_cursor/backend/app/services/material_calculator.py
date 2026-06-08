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

"""Детерминированный расчёт материалов."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AllowanceRule,
    AuxMaterialRule,
    CalculationItem,
    ExtractedFact,
    KimRule,
    KsiNode,
)
from app.services.process_analyzer import detect_process_type


async def calculate_materials(
    db: AsyncSession, calculation_id: uuid.UUID
) -> list[CalculationItem]:
    """Расчёт позиций материалов по КСИ и правилам КИМ/припусков."""
    old = (
        await db.execute(
            select(CalculationItem).where(CalculationItem.calculation_id == calculation_id)
        )
    ).scalars().all()
    for o in old:
        await db.delete(o)

    nodes = (
        await db.execute(select(KsiNode).where(KsiNode.calculation_id == calculation_id))
    ).scalars().all()
    kim_rules = (await db.execute(select(KimRule))).scalars().all()
    allowance_rules = (await db.execute(select(AllowanceRule))).scalars().all()
    aux_rules = (await db.execute(select(AuxMaterialRule))).scalars().all()

    items: list[CalculationItem] = []
    for node in nodes:
        if node.node_type == "assembly" and node.level == 0:
            continue
        material_name = "АМг6М"
        process_type = "cutting"
        if node.source_document_id:
            facts = (
                await db.execute(
                    select(ExtractedFact).where(
                        ExtractedFact.document_id == node.source_document_id,
                        ExtractedFact.field == "material",
                    )
                )
            ).scalars().all()
            if facts:
                material_name = facts[0].value
            process_type = await detect_process_type(db, node.source_document_id)

        kim = 0.78
        for r in kim_rules:
            if r.material_type in material_name or r.material_type == "sheet_metal":
                kim = r.kim_value
                break

        allowance = 0.1
        for r in allowance_rules:
            if r.material_type == "sheet_metal":
                allowance = r.allowance_value
                break

        net_qty = 1.0 * node.quantity_total
        gross_qty = round(net_qty / kim * (1 + allowance), 3)
        waste = round(gross_qty - net_qty, 3)

        item = CalculationItem(
            id=uuid.uuid4(),
            calculation_id=calculation_id,
            material_name=material_name[:255],
            net_qty=net_qty,
            gross_qty=gross_qty,
            unit="kg",
            kim=kim,
            allowance=allowance,
            waste=waste,
            formula=(
                f"gross = net({net_qty}) / kim({kim}) * (1 + allowance({allowance})) "
                f"= {gross_qty}; waste={waste}"
            ),
            rule_id="default_sheet",
            source_facts=[str(node.id)],
            confidence=0.84,
            requires_review=kim < 0.7,
            is_auxiliary=False,
        )
        db.add(item)
        items.append(item)

        for aux in aux_rules:
            if aux.process_type == process_type:
                aux_qty = round(net_qty * aux.rate_per_unit, 4)
                aux_item = CalculationItem(
                    id=uuid.uuid4(),
                    calculation_id=calculation_id,
                    material_name=aux.material_name[:255],
                    net_qty=aux_qty,
                    gross_qty=aux_qty,
                    unit=aux.unit,
                    kim=None,
                    allowance=None,
                    waste=0,
                    formula=f"aux = net_qty * {aux.rate_per_unit}",
                    rule_id=f"aux_{aux.process_type}",
                    source_facts=[str(node.id)],
                    confidence=0.9,
                    requires_review=False,
                    is_auxiliary=True,
                )
                db.add(aux_item)
                items.append(aux_item)

    await db.flush()
    return items
