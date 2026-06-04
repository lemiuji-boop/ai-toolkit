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

"""Схемы эндпоинта analyze."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.safety import SafetyShieldPayload

ComplexityLevel = Literal["L1", "L2", "L3", "L4"]


class AnalyzeRequest(BaseModel):
    """Запрос на анализ задачи."""

    project_name: str = Field(default="Untitled", description="Название проекта")
    task: str = Field(..., min_length=10, description="Описание задачи")
    context_lines: int = Field(
        default=0,
        ge=0,
        description="Число строк контекста (файлы) для оценки токенов",
    )


class AnalyzeResponse(BaseModel):
    """Ответ пайплайна MATFES."""

    complexity_level: ComplexityLevel
    feasibility_score: float = Field(ge=0.0, le=1.0)
    is_feasible: bool
    modified_options: list[dict[str, Any]] = Field(default_factory=list)
    estimated_tokens: dict[str, Any] = Field(default_factory=dict)
    cost_forecast_markdown: str
    final_markdown: str
    safety: SafetyShieldPayload
    selected_stack: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
