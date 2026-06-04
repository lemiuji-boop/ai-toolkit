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

"""Роутер сложности L1–L4."""

from typing import Any

from app.agents.state import AgentState
from app.config import ComplexityLevel


def router_node(state: AgentState) -> dict[str, Any]:
    """
    Анализ веса задачи по ключевым словам (ТЗ §4).

    L4: architect, creative, from scratch, r&d
    L3: algorithm, optimization, race condition
    L2: crud, endpoints, ui layout
    L1: default
    """
    task = state["user_task"].lower()
    level: ComplexityLevel = "L1"

    if any(
        k in task
        for k in ["architect", "creative", "from scratch", "engine from scratch", "r&d"]
    ):
        level = "L4"
    elif any(k in task for k in ["algorithm", "optimization", "race condition", "concurrency"]):
        level = "L3"
    elif any(
        k in task
        for k in ["crud", "endpoints", "ui layout", "api", "boilerplate", "рест"]
    ):
        level = "L2"

    # Длинные задачи повышают сложность
    if len(task) > 2000 and level == "L1":
        level = "L2"
    if state.get("context_lines", 0) > 500 and level in ("L1", "L2"):
        level = "L3"

    stack = {
        "Orchestration": "LangGraph / FastAPI",
        "AI_Infrastructure": f"Level {level} routing",
        "Client": "React Web (MVP)",
    }

    return {"complexity_level": level, "selected_stack": stack}
