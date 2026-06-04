#!/usr/bin/env python3
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

"""Ollama health and model availability checks."""
from __future__ import annotations

import asyncio
import sys

import httpx

from core.config import get_settings

PREFERRED_MODELS = ["llama3.2:3b", "qwen3:4b", "gemma3:4b"]


async def check_ollama(base_url: str | None = None) -> bool:
    settings = get_settings()
    url = (base_url or settings.ollama_base_url).rstrip("/")
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{url}/api/tags")
        return r.status_code == 200


async def list_model_names(base_url: str | None = None) -> list[str]:
    settings = get_settings()
    url = (base_url or settings.ollama_base_url).rstrip("/")
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{url}/api/tags")
        r.raise_for_status()
        return [m.get("name", "") for m in r.json().get("models", [])]


async def model_available(model: str, base_url: str | None = None) -> bool:
    """Точное совпадение тега Ollama (qwen3:8b ≠ qwen3:4b)."""
    names = await list_model_names(base_url)
    return any(n == model or n.startswith(f"{model}:") for n in names)


async def resolve_bench_model() -> str:
    """Первая доступная модель из preferred списка."""
    names = await list_model_names()
    for tag in PREFERRED_MODELS:
        for n in names:
            if n == tag or n.startswith(f"{tag}:"):
                return n
    raise RuntimeError(
        f"No bench model available. Pull one of: {', '.join(PREFERRED_MODELS)}"
    )


async def ensure_model(model: str, pull: bool = False) -> None:
    if await model_available(model):
        return
    if not pull:
        raise RuntimeError(f"Model {model} not available. Run: ollama pull {model}")
    import subprocess

    subprocess.run(["ollama", "pull", model], check=True)


def main() -> int:
    if not asyncio.run(check_ollama()):
        print("FAIL: Ollama not reachable", file=sys.stderr)
        return 1
    try:
        model = asyncio.run(resolve_bench_model())
    except RuntimeError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    print(f"OK: Ollama up, bench model={model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
