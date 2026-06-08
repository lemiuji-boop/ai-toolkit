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

from datetime import date, datetime

from pydantic import BaseModel


class DirectiveOut(BaseModel):
    id: int
    affected_doc_number: str | None
    backlog_action: str | None
    implementation_kind: str | None
    implementation_product: str | None
    implementation_date: date | None
    directive_text: str | None
    confidence: float | None

    model_config = {"from_attributes": True}


class ChangeOrderOut(BaseModel):
    id: int
    order_number: str
    issue_date: datetime | None
    description: str | None
    directives: list[DirectiveOut] = []

    model_config = {"from_attributes": True}


class AiStatusOut(BaseModel):
    label: str
    code: str
    percent: int


class CatalogRowOut(BaseModel):
    id: int
    doc_number: str
    name: str
    product_number: str | None
    doc_type: str
    status: str
    catalog_path: str | None
    version_index: str | None = None
    updated_at: datetime | None = None
    ai_status: AiStatusOut | None = None
    ai_insight: str | None = None

    model_config = {"from_attributes": True}


class CatalogListResponse(BaseModel):
    items: list[CatalogRowOut]
    total_count: int


class RevisionOut(BaseModel):
    id: int
    action: str
    changed_fields: dict
    user_id: int | None
    timestamp: datetime
    comment: str | None

    model_config = {"from_attributes": True}
