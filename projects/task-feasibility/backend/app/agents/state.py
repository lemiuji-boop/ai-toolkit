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

"""Состояние графа агентов."""

from typing import Any, NotRequired, TypedDict

from app.schemas.safety import SafetyShieldPayload


class AgentState(TypedDict):
    """Состояние LangGraph-пайплайна (ТЗ §4)."""

    user_task: str
    project_name: str
    context_lines: int
    complexity_level: str
    feasibility_score: float
    is_feasible: bool
    modified_options: list[dict[str, Any]]
    selected_stack: dict[str, Any]
    estimated_tokens: dict[str, Any]
    cost_forecast_markdown: str
    final_markdown: str
    safety: SafetyShieldPayload
    block_reason: NotRequired[str | None]
    warnings: NotRequired[list[str]]
    llm_notes: NotRequired[str]
    risks: NotRequired[list[str]]
    needs_pivot: NotRequired[bool]
