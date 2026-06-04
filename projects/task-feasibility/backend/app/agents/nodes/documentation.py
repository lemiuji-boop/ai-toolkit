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

"""Финальное техзадание."""

from typing import Any

from app.agents.state import AgentState
from app.config import ComplexityLevel
from app.llm.prompts.system import DOCS_SYSTEM
from app.llm.providers.base import ChatMessage
from app.llm.router import LLMRouter
from app.services.markdown_builder import build_assignment_markdown


async def documentation_node(state: AgentState) -> dict[str, Any]:
    """Сборка final_markdown."""
    level: ComplexityLevel = state.get("complexity_level", "L2")  # type: ignore[assignment]
    safety = state["safety"]
    router = LLMRouter()

    impl_steps = ""
    warnings = list(state.get("warnings") or [])

    try:
        messages = [
            ChatMessage(role="system", content=DOCS_SYSTEM),
            ChatMessage(
                role="user",
                content=f"Задача: {state['user_task']}\nУровень: {level}",
            ),
        ]
        resp = await router.complete(
            level,
            messages,
            encryption_required=safety.encryption_required,
            use_pruning=level == "L2",
        )
        impl_steps = "\n" + resp.content.strip()
        warnings.extend(router.warnings)
    except RuntimeError as exc:
        warnings.append(f"docs fallback: {exc}")
        impl_steps = "\n- Дополнительные шаги сформируйте после уточнения требований."

    stack = dict(state.get("selected_stack", {}))
    stack["FeasibilityIndex"] = f"{state.get('feasibility_score', 0):.2f}"

    md = build_assignment_markdown(
        project_name=state.get("project_name", "Untitled"),
        feasibility_score=state.get("feasibility_score", 0.0),
        complexity_level=level,
        selected_stack=stack,
        implementation_steps=impl_steps,
        cost_section=state.get("cost_forecast_markdown", ""),
        modified_options=state.get("modified_options", []),
    )

    return {"final_markdown": md, "warnings": warnings}
