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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import write_audit
from app.core.permissions import Perm, require_approve, require_permission
from app.core.revision_guard import assert_calculation_editable
from app.db.models import Calculation, CalculationRevision, Project, RevisionStatus, User
from app.db.session import get_db
from app.schemas.projects import (
    CalculationCreate,
    CalculationResponse,
    CalculationUpdate,
    RevisionCreate,
    RevisionResponse,
)

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.post("", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
async def create_calculation(
    body: CalculationCreate,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Calculation:
    project = await db.get(Project, body.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    calc = Calculation(
        id=uuid.uuid4(),
        project_id=body.project_id,
        title=body.title,
        designation=body.designation,
        created_by_id=user.id,
    )
    db.add(calc)
    rev = CalculationRevision(
        id=uuid.uuid4(),
        calculation_id=calc.id,
        revision_number=1,
        status=RevisionStatus.DRAFT,
        created_by_id=user.id,
    )
    db.add(rev)
    await write_audit(
        db, user_id=user.id, action="create", entity_type="calculation", entity_id=str(calc.id)
    )
    await db.commit()
    await db.refresh(calc)
    return calc


@router.get("/{calculation_id}", response_model=CalculationResponse)
async def get_calculation(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> Calculation:
    calc = await db.get(Calculation, calculation_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Расчёт не найден")
    return calc


@router.patch("/{calculation_id}", response_model=CalculationResponse)
async def update_calculation(
    calculation_id: uuid.UUID,
    body: CalculationUpdate,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Calculation:
    calc = await db.get(Calculation, calculation_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Расчёт не найден")
    await assert_calculation_editable(db, calculation_id)
    if body.title is not None:
        calc.title = body.title
    if body.designation is not None:
        calc.designation = body.designation
    await write_audit(
        db, user_id=user.id, action="update", entity_type="calculation", entity_id=str(calc.id)
    )
    await db.commit()
    await db.refresh(calc)
    return calc


@router.post("/{calculation_id}/revisions", response_model=RevisionResponse, status_code=201)
async def create_revision(
    calculation_id: uuid.UUID,
    body: RevisionCreate,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> CalculationRevision:
    calc = await db.get(Calculation, calculation_id)
    if not calc:
        raise HTTPException(status_code=404, detail="Расчёт не найден")
    max_num = await db.execute(
        select(func.max(CalculationRevision.revision_number)).where(
            CalculationRevision.calculation_id == calculation_id
        )
    )
    next_num = (max_num.scalar() or 0) + 1
    rev = CalculationRevision(
        id=uuid.uuid4(),
        calculation_id=calculation_id,
        revision_number=next_num,
        status=RevisionStatus.DRAFT,
        note=body.note,
        created_by_id=user.id,
    )
    db.add(rev)
    await write_audit(
        db,
        user_id=user.id,
        action="create",
        entity_type="calculation_revision",
        entity_id=str(rev.id),
    )
    await db.commit()
    await db.refresh(rev)
    return rev


@router.get("/{calculation_id}/revisions", response_model=list[RevisionResponse])
async def list_revisions(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[CalculationRevision]:
    result = await db.execute(
        select(CalculationRevision)
        .where(CalculationRevision.calculation_id == calculation_id)
        .order_by(CalculationRevision.revision_number.desc())
    )
    return list(result.scalars().all())


@router.post("/{calculation_id}/revisions/{revision_id}/approve", response_model=RevisionResponse)
async def approve_revision(
    calculation_id: uuid.UUID,
    revision_id: uuid.UUID,
    user: User = Depends(require_approve),
    db: AsyncSession = Depends(get_db),
) -> CalculationRevision:
    rev = await db.get(CalculationRevision, revision_id)
    if not rev or rev.calculation_id != calculation_id:
        raise HTTPException(status_code=404, detail="Ревизия не найдена")
    rev.status = RevisionStatus.APPROVED
    await write_audit(
        db,
        user_id=user.id,
        action="revision_approve",
        entity_type="calculation_revision",
        entity_id=str(rev.id),
    )
    await db.commit()
    await db.refresh(rev)
    return rev


@router.post("/{calculation_id}/revisions/{revision_id}/lock", response_model=RevisionResponse)
async def lock_revision(
    calculation_id: uuid.UUID,
    revision_id: uuid.UUID,
    user: User = Depends(require_approve),
    db: AsyncSession = Depends(get_db),
) -> CalculationRevision:
    rev = await db.get(CalculationRevision, revision_id)
    if not rev or rev.calculation_id != calculation_id:
        raise HTTPException(status_code=404, detail="Ревизия не найдена")
    rev.status = RevisionStatus.LOCKED
    await write_audit(
        db,
        user_id=user.id,
        action="revision_lock",
        entity_type="calculation_revision",
        entity_id=str(rev.id),
    )
    await db.commit()
    await db.refresh(rev)
    return rev
