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

"""RQ задачи обработки документов."""
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.models import Document, Job, JobStatus, StoredFile
from app.services.document_pipeline import run_document_pipeline
from app.services.jobs.events import emit_job_event, set_job_status

_engine = create_async_engine(settings.database_url.replace("postgresql://", "postgresql+psycopg://"))
_Session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


def process_document_job(job_id: str, file_ids: list[str]) -> None:
    """Синхронная точка входа RQ — запускает async пайплайн."""
    asyncio.run(_process_document_job_async(uuid.UUID(job_id), [uuid.UUID(f) for f in file_ids]))


async def _process_document_job_async(job_id: uuid.UUID, file_ids: list[uuid.UUID]) -> None:
    async with _Session() as db:
        job = await db.get(Job, job_id)
        if not job:
            return
        await set_job_status(db, job, JobStatus.RUNNING)
        await emit_job_event(db, job, "job_started", {"job_id": str(job_id)}, progress=0)
        await db.commit()

        try:
            total = max(len(file_ids), 1)
            for idx, fid in enumerate(file_ids):
                await db.refresh(job)
                if job.status in (JobStatus.CANCELLED, JobStatus.PAUSED):
                    break
                sf = await db.get(StoredFile, fid)
                if not sf:
                    continue
                await emit_job_event(
                    db,
                    job,
                    "file_processing",
                    {"file": sf.original_name, "index": idx + 1, "total": total},
                    progress=int((idx / total) * 80),
                )
                await db.commit()
                doc = await run_document_pipeline(db, sf, job)
                await emit_job_event(
                    db,
                    job,
                    "file_classified",
                    {
                        "file": sf.original_name,
                        "file_id": str(sf.id),
                        "document_id": str(doc.id),
                        "document_type": doc.document_type,
                    },
                    progress=int(((idx + 1) / total) * 90),
                )
                await emit_job_event(
                    db,
                    job,
                    "fact_extracted",
                    {"document_id": str(doc.id), "file_id": str(sf.id)},
                )
                await db.commit()

            document_ids = []
            if job.calculation_id:
                rows = await db.execute(
                    select(Document.id)
                    .join(StoredFile, Document.file_id == StoredFile.id)
                    .where(StoredFile.calculation_id == job.calculation_id)
                )
                document_ids = [str(r[0]) for r in rows.all()]

            await set_job_status(db, job, JobStatus.COMPLETED)
            await emit_job_event(
                db,
                job,
                "job_completed",
                {
                    "result_id": str(job_id),
                    "calculation_id": str(job.calculation_id) if job.calculation_id else None,
                    "document_ids": document_ids,
                },
                progress=100,
            )
        except Exception as exc:
            job.error_message = str(exc)
            await set_job_status(db, job, JobStatus.FAILED)
            await emit_job_event(db, job, "job_failed", {"error": str(exc)})
        await db.commit()
