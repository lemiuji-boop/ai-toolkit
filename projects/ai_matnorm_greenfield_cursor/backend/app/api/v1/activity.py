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

"""История действий и мониторинг расчёта."""
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Perm, require_permission
from app.db.models import AuditLog, Document, Job, JobEvent, JobStatus, StoredFile, User
from app.db.session import get_db

router = APIRouter(tags=["activity"])


class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    detail: str | None = None
    progress: int | None = None
    created_at: str


class CalculationOverview(BaseModel):
    calculation_id: uuid.UUID
    files_count: int
    jobs_running: int
    jobs_completed: int
    last_job_progress: int
    documents_count: int


@router.get("/calculations/{calculation_id}/activity", response_model=list[ActivityItem])
async def calculation_activity(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[ActivityItem]:
    items: list[ActivityItem] = []

    audits = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_id == str(calculation_id))
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    )
    for a in audits.scalars().all():
        items.append(
            ActivityItem(
                id=str(a.id),
                type="audit",
                title=f"{a.action}: {a.entity_type}",
                detail=str(a.payload) if a.payload else None,
                created_at=a.created_at.isoformat(),
            )
        )

    jobs = await db.execute(
        select(Job).where(Job.calculation_id == calculation_id).order_by(Job.created_at.desc())
    )
    for job in jobs.scalars().all():
        events = await db.execute(
            select(JobEvent)
            .where(JobEvent.job_id == job.id)
            .order_by(JobEvent.created_at.desc())
            .limit(20)
        )
        for ev in events.scalars().all():
            items.append(
                ActivityItem(
                    id=str(ev.id),
                    type=ev.event_type,
                    title=ev.event_type.replace("_", " ").title(),
                    detail=str(ev.payload) if ev.payload else None,
                    progress=job.progress_percent,
                    created_at=ev.created_at.isoformat(),
                )
            )

    files = await db.execute(
        select(StoredFile)
        .where(StoredFile.calculation_id == calculation_id)
        .order_by(StoredFile.created_at.desc())
        .limit(30)
    )
    for f in files.scalars().all():
        items.append(
            ActivityItem(
                id=str(f.id),
                type="file_uploaded",
                title=f.original_name,
                detail=f"{f.mime_type}, {f.size_bytes} байт",
                created_at=f.created_at.isoformat(),
            )
        )

    items.sort(key=lambda x: x.created_at, reverse=True)
    return items[:80]


@router.get("/calculations/{calculation_id}/overview", response_model=CalculationOverview)
async def calculation_overview(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> CalculationOverview:
    files_count = (
        await db.execute(
            select(StoredFile).where(StoredFile.calculation_id == calculation_id)
        )
    ).scalars().all()

    jobs = list(
        (
            await db.execute(
                select(Job)
                .where(Job.calculation_id == calculation_id)
                .order_by(Job.created_at.desc())
            )
        ).scalars().all()
    )

    running = sum(1 for j in jobs if j.status in (JobStatus.RUNNING, JobStatus.PENDING, JobStatus.PAUSED))
    completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
    last_progress = jobs[0].progress_percent if jobs else 0

    doc_count = 0
    if files_count:
        file_ids = [f.id for f in files_count]
        doc_count = len(
            (
                await db.execute(select(Document).where(Document.file_id.in_(file_ids)))
            ).scalars().all()
        )

    return CalculationOverview(
        calculation_id=calculation_id,
        files_count=len(files_count),
        jobs_running=running,
        jobs_completed=completed,
        last_job_progress=last_progress,
        documents_count=doc_count,
    )
