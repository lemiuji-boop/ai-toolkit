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

"""Генерация 3 альтернатив при низком FI."""

import json
import re
from typing import Any

from app.agents.state import AgentState
from app.config import ComplexityLevel
from app.llm.prompts.system import PIVOT_SYSTEM
from app.llm.providers.base import ChatMessage
from app.llm.router import LLMRouter


def _default_options(task: str) -> list[dict[str, str]]:
    """Статические альтернативы при недоступности LLM."""
    return [
        {
            "title": "MVP с урезанным scope",
            "scope": "Только core-функциональность без интеграций",
            "tradeoffs": "Быстрее, меньше рисков, меньше ценности",
        },
        {
            "title": "Поэтапная поставка",
            "scope": "Разбить задачу на 2–3 спринта",
            "tradeoffs": "Дольше до полного результата, ниже технический долг",
        },
        {
            "title": "Замена технологии",
            "scope": "Использовать готовые SaaS вместо custom-разработки",
            "tradeoffs": "Меньше гибкости, ниже стоимость разработки",
        },
    ]


async def pivot_redefine_node(state: AgentState) -> dict[str, Any]:
    """Три ветки modified_options."""
    if state.get("is_feasible", True) and not state.get("needs_pivot"):
        return {"modified_options": []}

    level: ComplexityLevel = state.get("complexity_level", "L2")  # type: ignore[assignment]
    safety = state["safety"]
    router = LLMRouter()

    prompt = (
        f"Задача: {state['user_task']}\n"
        f"FI: {state.get('feasibility_score', 0):.2f}\n"
        f"Риски: {state.get('risks', [])}"
    )
    messages = [
        ChatMessage(role="system", content=PIVOT_SYSTEM),
        ChatMessage(role="user", content=prompt),
    ]

    options: list[dict[str, Any]]
    warnings = list(state.get("warnings") or [])

    try:
        resp = await router.complete(
            level,
            messages,
            encryption_required=safety.encryption_required,
        )
        text = resp.content.strip()
        match = re.search(r"\{[\s\S]*\}", text)
        payload = json.loads(match.group() if match else text)
        options = payload.get("options", [])[:3]
        warnings.extend(router.warnings)
    except (json.JSONDecodeError, RuntimeError, KeyError) as exc:
        warnings.append(f"pivot fallback: {exc}")
        options = _default_options(state["user_task"])

    while len(options) < 3:
        options.append(_default_options(state["user_task"])[len(options) % 3])

    return {"modified_options": options[:3], "warnings": warnings}
