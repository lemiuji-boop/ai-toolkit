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

"""Задачи генерации."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.tasks import GenerationTask
from app.schemas.common import TaskResponse

router = APIRouter()


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    episode_id: UUID | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[GenerationTask]:
    """Список задач."""
    q = select(GenerationTask).order_by(GenerationTask.created_at)
    if episode_id:
        q = q.where(GenerationTask.episode_id == episode_id)
    result = await session.execute(q)
    return list(result.scalars().all())
