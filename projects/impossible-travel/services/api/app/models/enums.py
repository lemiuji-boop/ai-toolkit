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

"""Перечисления доменной модели."""

import enum


class EpisodeStatus(str, enum.Enum):
    """Статус выпуска."""

    DRAFT = "draft"
    GENERATING = "generating"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class GenerationTaskStatus(str, enum.Enum):
    """Статус задачи генерации."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class AssetType(str, enum.Enum):
    """Тип медиа-ассета."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    THUMBNAIL = "thumbnail"


class PublicationStatus(str, enum.Enum):
    """Статус публикации."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
