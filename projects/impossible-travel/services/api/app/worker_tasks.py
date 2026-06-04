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

"""Celery tasks."""

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.celery_app import celery_app
from app.db.session import async_session_factory
from app.models.tasks import GenerationTask
from app.orchestrator.pipeline import EpisodePipeline


@celery_app.task(bind=True, name="generate_episode_task")
def generate_episode_task(self, episode_id: str) -> dict:
    """Асинхронная генерация выпуска."""
    return asyncio.run(_run_pipeline(self.request.id, episode_id))


async def _run_pipeline(celery_task_id: str, episode_id: str) -> dict:
    pipeline = EpisodePipeline()
    eid = UUID(episode_id)

    async with async_session_factory() as session:
        result = await session.execute(
            select(GenerationTask).where(GenerationTask.episode_id == eid).limit(1)
        )
        task = result.scalar_one_or_none()
        if task:
            task.celery_task_id = celery_task_id
            await session.commit()

        await pipeline.run(session, eid)

    return {"episode_id": episode_id, "status": "completed"}
