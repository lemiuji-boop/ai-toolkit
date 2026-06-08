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
from datetime import date

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BacklogAction(str, enum.Enum):
    use = "use"
    rework = "rework"
    fix = "fix"
    scrap = "scrap"


class ImplementationKind(str, enum.Enum):
    from_product = "from_product"
    from_date = "from_date"
    immediate = "immediate"


class ChangeOrderDirective(Base):
    __tablename__ = "change_order_directives"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    change_order_id: Mapped[int] = mapped_column(ForeignKey("change_orders.id"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True, index=True)
    affected_doc_number: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    backlog_action: Mapped[BacklogAction | None] = mapped_column(Enum(BacklogAction), nullable=True, index=True)
    implementation_kind: Mapped[ImplementationKind | None] = mapped_column(Enum(ImplementationKind), nullable=True)
    implementation_product: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    implementation_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    directive_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    change_order: Mapped["ChangeOrder"] = relationship(back_populates="directives")
