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

"""Отчёты по расчёту."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Perm, require_permission
from app.db.models import CalculationItem, KsiNode, Report, User
from app.db.session import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreate(BaseModel):
    calculation_id: uuid.UUID
    revision_id: uuid.UUID | None = None
    title: str = "Отчёт по расчёту"


class ReportResponse(BaseModel):
    id: uuid.UUID
    calculation_id: uuid.UUID
    title: str
    content: dict

    model_config = {"from_attributes": True}


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(
    body: ReportCreate,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Report:
    items = (
        await db.execute(
            select(CalculationItem).where(CalculationItem.calculation_id == body.calculation_id)
        )
    ).scalars().all()
    nodes = (
        await db.execute(select(KsiNode).where(KsiNode.calculation_id == body.calculation_id))
    ).scalars().all()
    content = {
        "materials_count": len(items),
        "ksi_nodes_count": len(nodes),
        "items": [
            {"material": i.material_name, "gross_qty": i.gross_qty, "unit": i.unit} for i in items
        ],
    }
    report = Report(
        id=uuid.uuid4(),
        calculation_id=body.calculation_id,
        revision_id=body.revision_id,
        title=body.title,
        content=content,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/calculation/{calculation_id}", response_model=ReportResponse | None)
async def get_or_create_report_for_calculation(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> Report | None:
    existing = (
        await db.execute(
            select(Report)
            .where(Report.calculation_id == calculation_id)
            .order_by(Report.created_at.desc())
        )
    ).scalars().first()
    if existing:
        return existing
    body = ReportCreate(calculation_id=calculation_id)
    return await create_report(body, user, db)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> Report:
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден")
    return report
