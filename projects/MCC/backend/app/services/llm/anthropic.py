"""Провайдер Anthropic (Claude): Messages API, формат отличен от OpenAI.

Используется только для open-задач (FR-081: confidential → kind=local).
API-ключ передаётся заголовком x-api-key и НИКОГДА не логируется (SEC-002/003).
"""
from typing import Any

import httpx

from app.services.llm.base import ProviderInfo

# Версия API обязательна для Messages API (фиксирована, стабильная).
_ANTHROPIC_VERSION = "2023-06-01"
_MAX_TOKENS = 4096


class AnthropicProvider:
    def __init__(self, info: ProviderInfo, timeout: float = 120.0):
        self.info = info
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "anthropic-version": _ANTHROPIC_VERSION,
        }
        if self.info.api_key:
            h["x-api-key"] = self.info.api_key
        return h

    async def _chat(self, content: Any) -> str:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.info.base_url.rstrip('/')}/v1/messages",
                headers=self._headers(),
                json={
                    "model": self.info.model,
                    "max_tokens": _MAX_TOKENS,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            r.raise_for_status()
            blocks = r.json().get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")

    async def chat_text(self, prompt: str) -> str:
        return await self._chat(prompt)

    async def chat_vision(self, prompt: str, image_b64: str) -> str:
        content = [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": image_b64},
            },
            {"type": "text", "text": prompt},
        ]
        return await self._chat(content)
