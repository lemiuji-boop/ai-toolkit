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

"""Ассеты и промты."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetType


class Prompt(Base):
    """Сохранённый промт."""

    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"))
    shot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shots.id"), nullable=True)
    prompt_type: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    negative_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Asset(Base):
    """Медиа-файл в хранилище."""

    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"))
    shot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shots.id"), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(32))
    storage_key: Mapped[str] = mapped_column(String(1024))
    url: Mapped[str] = mapped_column(String(2048))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    episode: Mapped["Episode"] = relationship(back_populates="assets")  # type: ignore[name-defined]
