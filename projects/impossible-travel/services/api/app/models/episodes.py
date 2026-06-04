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

"""Выпуски, сцены, кадры."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EpisodeStatus


class Episode(Base):
    """Выпуск блога."""

    __tablename__ = "episodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    topic: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=EpisodeStatus.DRAFT.value)
    language: Mapped[str] = mapped_column(String(8), default="ru")
    duration_target: Mapped[int] = mapped_column(Integer, default=60)
    platforms: Mapped[list] = mapped_column(JSONB, default=list)
    style: Mapped[str] = mapped_column(String(256), default="photorealistic cinematic travel vlog")
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    main_character_id: Mapped[str] = mapped_column(String(64), default="main_girl")
    idea: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    worldbuilding: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    science_check: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    architect: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    shotlist: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    visual_style: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    platform_packages: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    compliance_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    quality_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    episode_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="episodes")  # type: ignore[name-defined]
    scenes: Mapped[list["Scene"]] = relationship(back_populates="episode", cascade="all, delete-orphan")
    shots: Mapped[list["Shot"]] = relationship(back_populates="episode", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="episode", cascade="all, delete-orphan")  # type: ignore[name-defined]
    generation_tasks: Mapped[list["GenerationTask"]] = relationship(  # type: ignore[name-defined]
        back_populates="episode", cascade="all, delete-orphan"
    )


class Scene(Base):
    """Сцена выпуска."""

    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255))
    time_range: Mapped[str | None] = mapped_column(String(32), nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)

    episode: Mapped["Episode"] = relationship(back_populates="scenes")


class Shot(Base):
    """Кадр раскадровки."""

    __tablename__ = "shots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"))
    scene_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scenes.id"), nullable=True)
    shot_external_id: Mapped[str] = mapped_column(String(32))
    duration: Mapped[int] = mapped_column(Integer, default=5)
    camera: Mapped[str | None] = mapped_column(String(256), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    visual_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    episode: Mapped["Episode"] = relationship(back_populates="shots")
