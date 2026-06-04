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

"""Сборка и запуск LangGraph."""

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from app.agents.nodes.cost import cost_estimator_node
from app.agents.nodes.documentation import documentation_node
from app.agents.nodes.feasibility import feasibility_node
from app.agents.nodes.pivot import pivot_redefine_node
from app.agents.nodes.router import router_node
from app.agents.state import AgentState
from app.config import get_settings
from app.guardrails.shield import SafetyShield
from app.schemas.safety import SafetyShieldPayload


def _route_after_feasibility(state: AgentState) -> Literal["pivot", "cost"]:
    """Условный переход: FI < threshold → pivot."""
    if state.get("needs_pivot"):
        return "pivot"
    return "cost"


def build_graph() -> Any:
    """Компиляция графа MATFES."""
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("feasibility", feasibility_node)
    graph.add_node("pivot", pivot_redefine_node)
    graph.add_node("cost", cost_estimator_node)
    graph.add_node("documentation", documentation_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "feasibility")
    graph.add_conditional_edges(
        "feasibility",
        _route_after_feasibility,
        {"pivot": "pivot", "cost": "cost"},
    )
    graph.add_edge("pivot", "cost")
    graph.add_edge("cost", "documentation")
    graph.add_edge("documentation", END)

    return graph.compile()


async def run_analysis(
    task: str,
    project_name: str,
    context_lines: int,
    safety: SafetyShieldPayload | None = None,
) -> AgentState:
    """Полный прогон пайплайна."""
    shield = SafetyShield()
    safety_result = safety or shield.scan(task)

    if safety_result.hard_blocked:
        raise ValueError(
            "Обнаружены credentials/секреты. Выполнение заблокировано.",
        )

    initial: AgentState = {
        "user_task": safety_result.sanitized_prompt,
        "project_name": project_name,
        "context_lines": context_lines,
        "complexity_level": "L1",
        "feasibility_score": 0.0,
        "is_feasible": False,
        "modified_options": [],
        "selected_stack": {},
        "estimated_tokens": {},
        "cost_forecast_markdown": "",
        "final_markdown": "",
        "safety": safety_result,
        "warnings": [],
    }

    compiled = build_graph()
    result: dict[str, Any] = await compiled.ainvoke(initial)
    return result  # type: ignore[return-value]
