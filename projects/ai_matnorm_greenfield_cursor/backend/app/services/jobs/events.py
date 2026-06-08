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
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job, JobEvent, JobStatus


async def emit_job_event(
    db: AsyncSession,
    job: Job,
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    progress: int | None = None,
) -> JobEvent:
    if progress is not None:
        job.progress_percent = progress
    event = JobEvent(
        id=uuid.uuid4(),
        job_id=job.id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    await db.flush()
    return event


async def set_job_status(db: AsyncSession, job: Job, status: JobStatus) -> None:
    job.status = status
    await db.flush()
