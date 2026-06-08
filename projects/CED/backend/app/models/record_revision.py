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

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RevisionTargetType(str, enum.Enum):
    document = "document"
    change_order = "change_order"
    directive = "directive"
    relation = "relation"


class RevisionAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"
    move = "move"


class RecordRevision(Base):
    __tablename__ = "record_revisions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_type: Mapped[RevisionTargetType] = mapped_column(Enum(RevisionTargetType), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(nullable=False, index=True)
    action: Mapped[RevisionAction] = mapped_column(Enum(RevisionAction), nullable=False)
    changed_fields: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
