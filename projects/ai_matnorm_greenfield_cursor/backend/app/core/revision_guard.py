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

"""Проверка блокировки расчёта по утверждённой ревизии."""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CalculationRevision, RevisionStatus


async def assert_calculation_editable(db: AsyncSession, calculation_id: uuid.UUID) -> None:
    """Запрет изменений при утверждённой или заблокированной последней ревизии."""
    result = await db.execute(
        select(CalculationRevision.status)
        .where(CalculationRevision.calculation_id == calculation_id)
        .order_by(CalculationRevision.revision_number.desc())
        .limit(1)
    )
    status_val = result.scalar_one_or_none()
    if status_val in (RevisionStatus.APPROVED, RevisionStatus.LOCKED):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Расчёт заблокирован утверждённой ревизией",
        )


async def get_latest_revision(
    db: AsyncSession, calculation_id: uuid.UUID
) -> CalculationRevision | None:
    result = await db.execute(
        select(CalculationRevision)
        .where(CalculationRevision.calculation_id == calculation_id)
        .order_by(CalculationRevision.revision_number.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
