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

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    file_id: UUID
    document_type: str
    is_scan: bool
    has_text_layer: bool
    page_count: int
    quality_score: float | None

    model_config = {"from_attributes": True}


class FactResponse(BaseModel):
    id: UUID
    document_id: UUID
    field: str
    value: str
    original_value: str | None = None
    normalized_value: str | None
    review_status: str = "pending"
    source_page: int | None
    bbox: list | None
    method: str
    confidence: float
    evidence_text: str | None
    is_user_corrected: bool
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FactUpdate(BaseModel):
    value: str
    reason: str | None = None
