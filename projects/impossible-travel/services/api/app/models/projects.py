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

"""Проект и бренд."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    """Корневой проект студии."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand_profile: Mapped["BrandProfile | None"] = relationship(back_populates="project", uselist=False)
    episodes: Mapped[list["Episode"]] = relationship(back_populates="project")  # type: ignore[name-defined]
    characters: Mapped[list["Character"]] = relationship(back_populates="project")  # type: ignore[name-defined]


class BrandProfile(Base):
    """Бренд и визуальная идентичность."""

    __tablename__ = "brand_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), unique=True)
    brand_voice: Mapped[str] = mapped_column(String(512), nullable=False)
    visual_identity: Mapped[str] = mapped_column(String(512), nullable=False)
    content_pillars: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="brand_profile")


class MonetizationLink(Base):
    """Ссылка монетизации (stub)."""

    __tablename__ = "monetization_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024))
    disclosed: Mapped[bool] = mapped_column(default=True)
