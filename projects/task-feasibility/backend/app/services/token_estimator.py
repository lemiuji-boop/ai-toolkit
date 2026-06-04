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

"""Оценка токенов и стоимости (ТЗ §5)."""

from typing import Any

from app.config import ComplexityLevel, Settings


# Итерации отладки по уровню
DEBUG_ITERATIONS: dict[ComplexityLevel, int] = {
    "L1": 1,
    "L2": 3,
    "L3": 8,
    "L4": 15,
}

# Ожидаемые строки генерируемого кода
ESTIMATED_OUTPUT_LINES: dict[ComplexityLevel, int] = {
    "L1": 50,
    "L2": 300,
    "L3": 800,
    "L4": 2000,
}

BASE_PROMPT_TOKENS = 800


def estimate_tokens(
    level: ComplexityLevel,
    context_lines: int,
    settings: Settings,
) -> dict[str, Any]:
    """
    Total_Input = (Base + context_lines * alpha) * debug_iterations
    Total_Output = output_lines * beta
    """
    alpha = settings.alpha_tokens_per_context_line
    beta = settings.beta_tokens_per_output_line
    debug_iters = DEBUG_ITERATIONS[level]
    output_lines = ESTIMATED_OUTPUT_LINES[level]

    input_raw = (BASE_PROMPT_TOKENS + context_lines * alpha) * debug_iters
    output_raw = output_lines * beta

    # L2+: prompt caching ~50% input
    cache_savings = 0.5 if level in ("L2", "L3", "L4") else 0.0
    input_cached = int(input_raw * (1 - cache_savings * 0.9))
    input_billed = int(input_raw * (1 - cache_savings) + input_cached * cache_savings * 0.5)

    return {
        "complexity_level": level,
        "debug_iterations": debug_iters,
        "input_tokens_raw": int(input_raw),
        "input_tokens_billed": input_billed,
        "output_tokens": int(output_raw),
        "cache_applied": level in ("L2", "L3", "L4"),
        "context_lines": context_lines,
    }


def estimate_cost_usd(
    tokens: dict[str, Any],
    settings: Settings,
    *,
    production_inquiries_per_1k: int = 1000,
) -> dict[str, float]:
    """Расчёт USD по тарифам из настроек."""
    inp = tokens["input_tokens_billed"]
    out = tokens["output_tokens"]
    cached = tokens.get("cache_applied", False)

    price_in = settings.price_input_per_million
    price_out = settings.price_output_per_million
    if cached:
        price_in = (price_in + settings.price_cached_input_per_million) / 2

    dev_cost = (inp / 1_000_000) * price_in + (out / 1_000_000) * price_out
    # Production: ~10% dev tokens на 1000 запросов (эвристика)
    prod_tokens = int((inp + out) * 0.1)
    prod_cost = (prod_tokens / 1_000_000) * price_in

    return {
        "development_usd": round(dev_cost, 2),
        "production_per_1k_inquiries_usd": round(prod_cost, 2),
        "production_tokens_estimate": prod_tokens,
    }


def format_cost_markdown(
    level: ComplexityLevel,
    tokens: dict[str, Any],
    costs: dict[str, float],
    settings: Settings,
    primary_tool: str,
    auxiliary: str,
) -> str:
    """Markdown-блок прогноза (ТЗ §5)."""
    cache_note = "Да -> экономия применена" if tokens.get("cache_applied") else "Нет"
    return f"""### Estimated Token Allocation & Pricing Forecast
* **Primary Tool Assigned:** {primary_tool}
* **Auxiliary Reviewer Node:** {auxiliary}
* **Development Phase Cost:**
    * Input: ~{tokens['input_tokens_billed']:,} tokens (Cached: {cache_note})
    * Output: ~{tokens['output_tokens']:,} tokens
    * Debug iterations: {tokens['debug_iterations']}
    * Estimated API Outlay: **${costs['development_usd']:.2f} USD**
* **Production Phase Cost (Per 1,000 user inquiries):** ~{costs['production_tokens_estimate']:,} tokens (**${costs['production_per_1k_inquiries_usd']:.2f} USD**)
* **Complexity Level:** {level}
"""
