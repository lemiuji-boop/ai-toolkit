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

"""Роутер выпусков."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import EpisodeStatus
from app.models.episodes import Episode
from app.schemas.episodes import (
    ApproveResponse,
    EpisodeCreate,
    EpisodeDetail,
    EpisodeSummary,
    GenerateResponse,
)
from app.services.episodes import create_episode, get_episode_detail

router = APIRouter()


@router.get("", response_model=list[EpisodeSummary])
async def list_episodes(
    status: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[Episode]:
    """Список выпусков."""
    q = select(Episode).order_by(Episode.created_at.desc())
    if status:
        q = q.where(Episode.status == status)
    result = await session.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=EpisodeSummary, status_code=201)
async def post_episode(
    data: EpisodeCreate,
    session: AsyncSession = Depends(get_db),
) -> Episode:
    """Создать выпуск."""
    return await create_episode(session, data)


@router.get("/{episode_id}", response_model=EpisodeDetail)
async def get_episode(
    episode_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> Episode:
    """Детали выпуска."""
    episode = await get_episode_detail(session, episode_id)
    if not episode:
        raise HTTPException(404, "Episode not found")
    return episode


@router.post("/{episode_id}/generate", response_model=GenerateResponse)
async def generate_episode(
    episode_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> GenerateResponse:
    """Запуск полного пайплайна через Celery."""
    episode = await session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(404, "Episode not found")
    if episode.status == EpisodeStatus.GENERATING.value:
        raise HTTPException(409, "Generation already in progress")

    episode.status = EpisodeStatus.GENERATING.value
    await session.flush()

    from app.worker_tasks import generate_episode_task

    async_result = generate_episode_task.delay(str(episode_id))
    return GenerateResponse(
        episode_id=episode_id,
        celery_task_id=async_result.id,
        message="Генерация запущена",
    )


@router.post("/{episode_id}/approve", response_model=ApproveResponse)
async def approve_episode(
    episode_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ApproveResponse:
    """Утвердить выпуск."""
    episode = await session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(404, "Episode not found")
    if episode.status != EpisodeStatus.READY_FOR_REVIEW.value:
        raise HTTPException(
            409,
            f"Cannot approve from status {episode.status}",
        )
    episode.status = EpisodeStatus.APPROVED.value
    return ApproveResponse(episode_id=episode_id, status=episode.status)


@router.post("/{episode_id}/publish", response_model=ApproveResponse)
async def publish_episode(
    episode_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ApproveResponse:
    """Stub публикации (MVP — только смена статуса)."""
    episode = await session.get(Episode, episode_id)
    if not episode:
        raise HTTPException(404, "Episode not found")
    if episode.status not in (
        EpisodeStatus.APPROVED.value,
        EpisodeStatus.SCHEDULED.value,
    ):
        raise HTTPException(409, "Episode must be approved first")
    episode.status = EpisodeStatus.PUBLISHED.value
    return ApproveResponse(episode_id=episode_id, status=episode.status)
