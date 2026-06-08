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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Perm, require_permission
from app.db.models import KsiNode, User
from app.db.session import get_db
from app.services.ksi_builder import build_ksi_from_calculation

router = APIRouter(prefix="/ksi", tags=["ksi"])


class KsiNodeResponse(BaseModel):
    id: uuid.UUID
    calculation_id: uuid.UUID
    parent_id: uuid.UUID | None
    level: int
    designation: str
    name: str
    node_type: str
    quantity_per_parent: float
    quantity_total: float
    confidence: float

    model_config = {"from_attributes": True}


class KsiBuildRequest(BaseModel):
    calculation_id: uuid.UUID


class KsiNodePatch(BaseModel):
    designation: str | None = None
    name: str | None = None
    quantity_per_parent: float | None = None
    quantity_total: float | None = None


@router.post("/build", response_model=list[KsiNodeResponse])
async def build_ksi(
    body: KsiBuildRequest,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> list[KsiNode]:
    nodes = await build_ksi_from_calculation(db, body.calculation_id)
    await db.commit()
    return nodes


@router.get("/{calculation_id}", response_model=list[KsiNodeResponse])
async def get_ksi(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[KsiNode]:
    result = await db.execute(
        select(KsiNode).where(KsiNode.calculation_id == calculation_id)
    )
    return list(result.scalars().all())


@router.patch("/nodes/{node_id}", response_model=KsiNodeResponse)
async def patch_ksi_node(
    node_id: uuid.UUID,
    body: KsiNodePatch,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> KsiNode:
    node = await db.get(KsiNode, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Узел КСИ не найден")
    if body.designation is not None:
        node.designation = body.designation
    if body.name is not None:
        node.name = body.name
    if body.quantity_per_parent is not None:
        node.quantity_per_parent = body.quantity_per_parent
    if body.quantity_total is not None:
        node.quantity_total = body.quantity_total
    await db.commit()
    await db.refresh(node)
    return node


class KsiChildCreate(BaseModel):
    designation: str
    name: str
    node_type: str = "detail"
    quantity_per_parent: float = 1.0


@router.post("/nodes/{node_id}/children", response_model=KsiNodeResponse, status_code=201)
async def add_ksi_child(
    node_id: uuid.UUID,
    body: KsiChildCreate,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> KsiNode:
    parent = await db.get(KsiNode, node_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Родительский узел не найден")
    from app.core.revision_guard import assert_calculation_editable

    await assert_calculation_editable(db, parent.calculation_id)
    child = KsiNode(
        id=uuid.uuid4(),
        calculation_id=parent.calculation_id,
        parent_id=parent.id,
        level=parent.level + 1,
        designation=body.designation,
        name=body.name,
        node_type=body.node_type,
        quantity_per_parent=body.quantity_per_parent,
        quantity_total=round(parent.quantity_total * body.quantity_per_parent, 4),
        confidence=1.0,
    )
    db.add(child)
    await db.commit()
    await db.refresh(child)
    return child
