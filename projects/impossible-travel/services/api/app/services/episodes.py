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

"""Сервис выпусков."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.episodes import Episode
from app.models.projects import Project
from app.schemas.episodes import EpisodeCreate


async def get_default_project_id(session: AsyncSession) -> UUID:
    """Возвращает ID первого проекта."""
    result = await session.execute(select(Project).limit(1))
    project = result.scalar_one_or_none()
    if not project:
        raise RuntimeError("No project seeded. Run migrations and restart API.")
    return project.id


async def create_episode(session: AsyncSession, data: EpisodeCreate) -> Episode:
    """Создаёт новый выпуск."""
    project_id = await get_default_project_id(session)
    episode = Episode(
        project_id=project_id,
        topic=data.topic,
        duration_target=data.duration_target,
        platforms=data.platforms,
        language=data.language,
        style=data.style,
        main_character_id=data.main_character_id,
    )
    session.add(episode)
    await session.flush()
    await session.refresh(episode)
    return episode


async def get_episode_detail(session: AsyncSession, episode_id: UUID) -> Episode | None:
    """Загружает выпуск со связями."""
    result = await session.execute(
        select(Episode)
        .where(Episode.id == episode_id)
        .options(
            selectinload(Episode.assets),
            selectinload(Episode.generation_tasks),
        )
    )
    return result.scalar_one_or_none()
