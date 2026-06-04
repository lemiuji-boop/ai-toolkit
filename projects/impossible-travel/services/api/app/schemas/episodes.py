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

"""Схемы выпусков."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AssetResponse, ORMBase, TaskResponse


class EpisodeCreate(BaseModel):
    """Создание выпуска."""

    topic: str = Field(..., min_length=2, max_length=512)
    duration_target: int = Field(60, ge=30, le=90)
    platforms: list[str] = Field(
        default_factory=lambda: ["instagram", "tiktok", "youtube_shorts"]
    )
    language: str = "ru"
    style: str = "photorealistic cinematic travel vlog"
    main_character_id: str = "main_girl"


class EpisodeSummary(ORMBase):
    """Краткий выпуск."""

    id: UUID
    topic: str
    title: str | None
    status: str
    language: str
    duration_target: int
    platforms: list
    created_at: datetime
    updated_at: datetime


class EpisodeDetail(EpisodeSummary):
    """Полный выпуск."""

    style: str
    location_id: UUID | None
    main_character_id: str
    idea: dict | None
    worldbuilding: dict | None
    science_check: dict | None
    architect: dict | None
    script: str | None
    shotlist: list | None
    visual_style: dict | None
    platform_packages: dict | None
    compliance_report: dict | None
    quality_report: dict | None
    episode_metadata: dict | None
    assets: list[AssetResponse] = []
    generation_tasks: list[TaskResponse] = []


class GenerateResponse(BaseModel):
    """Ответ на запуск генерации."""

    episode_id: UUID
    celery_task_id: str
    message: str = "Генерация запущена"


class ApproveResponse(BaseModel):
    """Ответ на утверждение."""

    episode_id: UUID
    status: str
