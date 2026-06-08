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

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.permissions import Perm, get_current_user, require_permission
from app.db.models import Job, JobEvent, JobStatus, User
from app.db.session import AsyncSessionLocal, get_db
from app.schemas.jobs import JobCreateRequest, JobEventResponse, JobResponse
from app.services.jobs.events import emit_job_event, set_job_status
from app.workers.rq_app import get_queue
from app.workers.tasks import process_document_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/document-processing", response_model=JobResponse, status_code=201)
async def start_document_processing(
    body: JobCreateRequest,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Job:
    job = Job(
        id=uuid.uuid4(),
        calculation_id=body.calculation_id,
        job_type="document_processing",
        status=JobStatus.PENDING,
        created_by_id=user.id,
    )
    db.add(job)
    await emit_job_event(db, job, "job_queued", {"calculation_id": str(body.calculation_id)})
    await db.commit()
    await db.refresh(job)

    try:
        q = get_queue()
        rq_job = q.enqueue(
            process_document_job,
            str(job.id),
            [str(f) for f in body.file_ids],
            job_timeout=3600,
        )
        job.rq_job_id = rq_job.id
        await db.commit()
    except Exception as exc:
        job.error_message = f"Очередь недоступна: {exc}"
        await set_job_status(db, job, JobStatus.FAILED)
        await db.commit()

    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Job:
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return job


@router.get("/{job_id}/events", response_model=list[JobEventResponse])
async def list_job_events(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobEvent]:
    result = await db.execute(
        select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at)
    )
    return list(result.scalars().all())


@router.get("/{job_id}/stream")
async def stream_job_events(
    job_id: uuid.UUID,
    token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    user: User | None = None
    # SSE не передаёт Authorization — допускаем token в query
    if token:
        from app.core.security import get_subject_from_token
        from app.db.models import User as UserModel

        try:
            uid = get_subject_from_token(token, "access")
            user = await db.get(UserModel, uid)
        except Exception:
            raise HTTPException(status_code=401, detail="Невалидный токен")
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    async def event_generator() -> AsyncGenerator[dict, None]:
        last_count = 0
        while True:
            async with AsyncSessionLocal() as db:
                job = await db.get(Job, job_id)
                if not job:
                    yield {"event": "error", "data": json.dumps({"detail": "not found"})}
                    break
                result = await db.execute(
                    select(JobEvent)
                    .where(JobEvent.job_id == job_id)
                    .order_by(JobEvent.created_at)
                )
                events = list(result.scalars().all())
                for ev in events[last_count:]:
                    yield {
                        "event": ev.event_type,
                        "data": json.dumps(
                            {
                                "type": ev.event_type,
                                "job_id": str(job_id),
                                "payload": ev.payload,
                            },
                            ensure_ascii=False,
                        ),
                    }
                last_count = len(events)
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    yield {
                        "event": "stream_end",
                        "data": json.dumps({"status": job.status.value}),
                    }
                    break
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


@router.post("/{job_id}/pause")
async def pause_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await set_job_status(db, job, JobStatus.PAUSED)
    await emit_job_event(db, job, "job_paused", {})
    await db.commit()
    return {"status": "paused"}


@router.post("/{job_id}/resume")
async def resume_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await set_job_status(db, job, JobStatus.RUNNING)
    await emit_job_event(db, job, "job_resumed", {})
    await db.commit()
    return {"status": "running"}


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await set_job_status(db, job, JobStatus.CANCELLED)
    await emit_job_event(db, job, "job_cancelled", {})
    if job.rq_job_id:
        try:
            from rq.job import Job as RqJob

            rq_job = RqJob.fetch(job.rq_job_id, connection=get_queue().connection)
            rq_job.cancel()
        except Exception:
            pass
    await db.commit()
    return {"status": "cancelled"}
