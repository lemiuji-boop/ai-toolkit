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

"""Ollama API client with timing metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from core.config import get_settings


@dataclass
class OllamaMetrics:
    tok_per_sec: float
    ttft_ms: float
    prompt_tokens: int
    eval_tokens: int
    total_ms: float
    raw: dict[str, Any]


@dataclass
class OllamaResponse:
    text: str
    metrics: OllamaMetrics


class OllamaClient:
    """HTTP client for Ollama generate/chat."""

    def __init__(self, base_url: str | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            models = r.json().get("models", [])
            return [m.get("name", "") for m in models]

    async def unload_model(self, model: str) -> None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": "", "keep_alive": 0},
            )
            if r.status_code not in (200, 404):
                r.raise_for_status()

    async def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int = 42,
        num_ctx: int = 4096,
        num_predict: int = 256,
    ) -> OllamaResponse:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "seed": seed,
                "num_ctx": num_ctx,
                "num_predict": num_predict,
            },
        }
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=600.0) as client:
            r = await client.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
        return OllamaResponse(text=data.get("response", ""), metrics=_parse_metrics(data))


def _parse_metrics(data: dict[str, Any]) -> OllamaMetrics:
  eval_count = int(data.get("eval_count") or 0)
  eval_ns = int(data.get("eval_duration") or 0)
  prompt_count = int(data.get("prompt_eval_count") or 0)
  prompt_ns = int(data.get("prompt_eval_duration") or 0)
  total_ns = int(data.get("total_duration") or 0)
  tok_per_sec = (eval_count / (eval_ns / 1e9)) if eval_ns > 0 else 0.0
  ttft_ms = prompt_ns / 1e6 if prompt_ns else 0.0
  total_ms = total_ns / 1e6 if total_ns else 0.0
  return OllamaMetrics(
      tok_per_sec=tok_per_sec,
      ttft_ms=ttft_ms,
      prompt_tokens=prompt_count,
      eval_tokens=eval_count,
      total_ms=total_ms,
      raw=data,
  )
