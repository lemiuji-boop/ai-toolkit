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

"""Оценка токенов и стоимости."""

from typing import Any

from app.agents.state import AgentState
from app.config import ComplexityLevel, get_settings
from app.services.token_estimator import (
    estimate_cost_usd,
    estimate_tokens,
    format_cost_markdown,
)


def cost_estimator_node(state: AgentState) -> dict[str, Any]:
    """Чистая математика + markdown прогноз."""
    settings = get_settings()
    level: ComplexityLevel = state.get("complexity_level", "L2")  # type: ignore[assignment]
    context_lines = state.get("context_lines", 0)

    tokens = estimate_tokens(level, context_lines, settings)
    costs = estimate_cost_usd(tokens, settings)

    primary = f"{settings.get_model(level)} ({'Ollama' if level == 'L1' else 'Cloud API'})"
    auxiliary = f"Ollama / {settings.model_l1} (Local, $0.00 cost)"

    md = format_cost_markdown(
        level, tokens, costs, settings, primary, auxiliary
    )

    return {
        "estimated_tokens": {**tokens, **costs},
        "cost_forecast_markdown": md,
    }
