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

"""Оценка feasibility index."""

import json
import re
from typing import Any

from app.agents.state import AgentState
from app.config import ComplexityLevel, get_settings
from app.llm.prompts.system import FEASIBILITY_SYSTEM
from app.llm.providers.base import ChatMessage
from app.llm.router import LLMRouter


def _heuristic_fi(task: str, level: ComplexityLevel) -> dict[str, Any]:
    """Fallback без LLM."""
    base = 0.85
    if level == "L4":
        base = 0.55
    elif level == "L3":
        base = 0.7
    if any(w in task.lower() for w in ["impossible", "невозможно", "quantum", "agi"]):
        base = 0.35
    return {
        "feasibility_score": base,
        "risks": ["Оценка эвристическая — LLM недоступен"],
        "blockers": [],
        "summary": "Эвристическая оценка MATFES",
    }


def _parse_json_content(text: str) -> dict[str, Any]:
    """Извлечение JSON из ответа модели."""
    text = text.strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group())
    return json.loads(text)


async def feasibility_node(state: AgentState) -> dict[str, Any]:
    """Вычисляет FI; при FI < threshold — needs_pivot."""
    settings = get_settings()
    level: ComplexityLevel = state.get("complexity_level", "L2")  # type: ignore[assignment]
    safety = state["safety"]
    router = LLMRouter()

    prompt = (
        f"Задача:\n{state['user_task']}\n\n"
        f"Уровень сложности: {level}\n"
        f"Строк контекста: {state.get('context_lines', 0)}"
    )
    messages = [
        ChatMessage(role="system", content=FEASIBILITY_SYSTEM),
        ChatMessage(role="user", content=prompt),
    ]

    data: dict[str, Any]
    warnings: list[str] = list(state.get("warnings") or [])

    try:
        resp = await router.complete(
            level,
            messages,
            encryption_required=safety.encryption_required,
            use_pruning=level == "L2",
        )
        data = _parse_json_content(resp.content)
        warnings.extend(router.warnings)
    except (json.JSONDecodeError, RuntimeError, KeyError) as exc:
        warnings.append(f"feasibility fallback: {exc}")
        data = _heuristic_fi(state["user_task"], level)

    score = float(data.get("feasibility_score", 0.5))
    score = max(0.0, min(1.0, score))
    threshold = settings.feasibility_threshold
    is_feasible = score >= threshold

    return {
        "feasibility_score": score,
        "is_feasible": is_feasible,
        "needs_pivot": not is_feasible,
        "risks": data.get("risks", []),
        "llm_notes": data.get("summary", ""),
        "warnings": warnings,
    }
