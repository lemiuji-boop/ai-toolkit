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

from pydantic import BaseModel, Field


class DocumentClassificationOut(BaseModel):
    document_type: str = Field(description="тип документа")
    confidence: float = Field(ge=0, le=1)
    language: str = "ru"


class FactVerificationOut(BaseModel):
    field: str
    value: str
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = False
