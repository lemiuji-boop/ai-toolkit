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

"""LLM-as-judge (local Ollama or anthropic)."""
from __future__ import annotations

import json
import re

import httpx

from bench.ollama_client import OllamaClient
from core.config import get_settings

JUDGE_PROMPT_RU = """Оцени ответ модели по шкале 0-5 по критерию качества.
Верни JSON: {{"score": <0-5>, "rationale": "<кратко по-русски>"}}

Задание: {prompt}
Ответ модели: {output}
"""


async def _resolve_judge_model() -> str:
    from scripts.ollama_preflight import model_available, resolve_bench_model

    settings = get_settings()
    if await model_available(settings.judge_local_model):
        return settings.judge_local_model
    return await resolve_bench_model()


async def judge_output(
    prompt: str, output: str
) -> tuple[float, dict[str, object], str | None]:
    settings = get_settings()
    if settings.judge_mode == "anthropic" and settings.anthropic_api_key:
        return await _judge_anthropic(prompt, output, settings.anthropic_api_key)
    client = OllamaClient()
    judge_model = await _resolve_judge_model()
    judge_prompt = JUDGE_PROMPT_RU.format(prompt=prompt[:2000], output=output[:3000])
    resp = await client.generate(
        judge_model,
        judge_prompt,
        temperature=0.0,
        num_predict=256,
    )
    return _parse_judge_response(resp.text)


async def _judge_anthropic(
    prompt: str, output: str, api_key: str
) -> tuple[float, dict[str, object], str | None]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 256,
                "messages": [
                    {
                        "role": "user",
                        "content": JUDGE_PROMPT_RU.format(prompt=prompt, output=output),
                    }
                ],
            },
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"]
    return _parse_judge_response(text)


def _parse_judge_response(text: str) -> tuple[float, dict[str, object], str | None]:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        obj = json.loads(text[start:end])
        score = float(obj.get("score", 0)) / 5.0
        rationale = obj.get("rationale")
        return score, obj, rationale
    except Exception:
        m = re.search(r"score[\"']?\s*:\s*(\d)", text, re.I)
        if m:
            return float(m.group(1)) / 5.0, {"raw": text}, None
        return 0.5, {"raw": text}, "parse failed"
