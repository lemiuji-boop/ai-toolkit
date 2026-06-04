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

"""Общие схемы."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Базовая схема с ORM mode."""

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Ответ health check."""

    status: str = "ok"


class SettingsResponse(BaseModel):
    """Публичные настройки."""

    mock_generation: bool
    app_env: str
    max_daily_generation_cost_usd: float


class SettingsUpdate(BaseModel):
    """Обновление настроек (ограниченно в MVP)."""

    mock_generation: bool | None = None


class TaskResponse(ORMBase):
    """Задача генерации."""

    id: UUID
    episode_id: UUID
    step: str
    status: str
    progress: float
    error: str | None
    celery_task_id: str | None
    created_at: datetime
    updated_at: datetime


class AssetResponse(ORMBase):
    """Медиа-ассет."""

    id: UUID
    episode_id: UUID
    shot_id: UUID | None
    asset_type: str
    storage_key: str
    url: str
    meta: dict
    created_at: datetime


class CharacterResponse(ORMBase):
    """Персонаж."""

    id: UUID
    project_id: UUID
    external_id: str
    name: str
    role: str
    bible: dict
    created_at: datetime


class LocationResponse(ORMBase):
    """Локация."""

    id: UUID
    project_id: UUID
    episode_id: UUID | None
    name: str
    location_type: str
    data: dict
    created_at: datetime
