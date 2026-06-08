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
from app.db.models import AllowanceRule, CalculationItem, KimRule, Material, User
from app.db.session import get_db
from app.services.material_calculator import calculate_materials

router = APIRouter(prefix="/materials", tags=["materials"])


class MaterialResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    material_type: str
    unit: str

    model_config = {"from_attributes": True}


class CalculationItemResponse(BaseModel):
    id: uuid.UUID
    material_name: str
    net_qty: float
    gross_qty: float
    unit: str
    kim: float | None
    allowance: float | None
    waste: float | None
    formula: str
    confidence: float
    requires_review: bool

    model_config = {"from_attributes": True}


class CalculateRequest(BaseModel):
    calculation_id: uuid.UUID


class MaterialCreate(BaseModel):
    code: str
    name: str
    material_type: str
    unit: str = "kg"


@router.post("", response_model=MaterialResponse, status_code=201)
async def create_material(
    body: MaterialCreate,
    user: User = Depends(require_permission(Perm.ADMIN.value)),
    db: AsyncSession = Depends(get_db),
) -> Material:
    mat = Material(
        id=uuid.uuid4(),
        code=body.code,
        name=body.name,
        material_type=body.material_type,
        unit=body.unit,
    )
    db.add(mat)
    await db.commit()
    await db.refresh(mat)
    return mat


@router.get("", response_model=list[MaterialResponse])
async def list_materials(
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[Material]:
    result = await db.execute(select(Material))
    return list(result.scalars().all())


@router.post("/calculate", response_model=list[CalculationItemResponse])
async def run_calculate(
    body: CalculateRequest,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> list[CalculationItem]:
    items = await calculate_materials(db, body.calculation_id)
    await db.commit()
    return items


@router.get("/results/{calculation_id}", response_model=list[CalculationItemResponse])
async def get_results(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[CalculationItem]:
    result = await db.execute(
        select(CalculationItem).where(CalculationItem.calculation_id == calculation_id)
    )
    return list(result.scalars().all())


class KimRuleCreate(BaseModel):
    material_type: str
    process_type: str
    kim_value: float
    description: str = ""


@router.post("/kim-rules", response_model=dict)
async def create_kim_rule(
    body: KimRuleCreate,
    user: User = Depends(require_permission(Perm.ADMIN.value)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rule = KimRule(
        id=uuid.uuid4(),
        material_type=body.material_type,
        process_type=body.process_type,
        kim_value=body.kim_value,
        description=body.description,
    )
    db.add(rule)
    await db.commit()
    return {"id": str(rule.id)}
