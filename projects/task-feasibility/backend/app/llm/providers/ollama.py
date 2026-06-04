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

"""Провайдер Ollama (локальный L1)."""

import httpx

from app.config import get_settings
from app.llm.providers.base import ChatMessage, LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Локальный inference через Ollama API."""

    name = "ollama"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._base = self._settings.ollama_base_url.rstrip("/")

    async def is_available(self) -> bool:
        """GET /api/tags — список моделей."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base}/api/tags")
                return resp.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        max_tokens: int,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """POST /api/chat."""
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self._base}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = data.get("message", {}).get("content", "")
        eval_count = data.get("eval_count", 0)
        prompt_eval = data.get("prompt_eval_count", 0)
        return LLMResponse(
            content=content,
            model=model,
            provider=self.name,
            input_tokens=prompt_eval,
            output_tokens=eval_count,
        )

    async def list_models(self) -> list[str]:
        """Список установленных моделей."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base}/api/tags")
                resp.raise_for_status()
                models = resp.json().get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except (httpx.HTTPError, OSError):
            return []
