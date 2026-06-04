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

"""OpenAI-совместимый облачный провайдер."""

import httpx

from app.config import get_settings
from app.llm.providers.base import ChatMessage, LLMProvider, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    """Клиент для OpenAI / DeepSeek / совместимых API."""

    name = "cloud"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._base = self._settings.cloud_api_base.rstrip("/")
        self._key = self._settings.cloud_api_key

    async def is_available(self) -> bool:
        """Доступен при наличии API key."""
        return bool(self._key.strip())

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        max_tokens: int,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """POST /chat/completions."""
        if not self._key:
            raise RuntimeError("CLOUD_API_KEY не задан")

        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        url = f"{self._base}/chat/completions"
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return LLMResponse(
            content=choice or "",
            model=model,
            provider=self.name,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
