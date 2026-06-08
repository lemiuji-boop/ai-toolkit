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

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str
    owner_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CalculationCreate(BaseModel):
    project_id: UUID
    title: str
    designation: str = ""


class CalculationUpdate(BaseModel):
    title: str | None = None
    designation: str | None = None


class CalculationResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    designation: str
    created_by_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class RevisionCreate(BaseModel):
    note: str = ""


class RevisionResponse(BaseModel):
    id: UUID
    calculation_id: UUID
    revision_number: int
    status: str
    note: str
    created_by_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
