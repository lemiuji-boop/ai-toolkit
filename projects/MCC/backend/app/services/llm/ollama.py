"""Локальный провайдер Ollama (chat API, format=json, temperature=0)."""
import httpx

from app.services.llm.base import ProviderInfo


class OllamaProvider:
    def __init__(self, info: ProviderInfo, timeout: float = 120.0):
        self.info = info
        self._timeout = timeout

    async def _chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.info.base_url.rstrip('/')}/api/chat",
                json={
                    "model": self.info.model,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                    "messages": messages,
                },
            )
            r.raise_for_status()
            return r.json()["message"]["content"]

    async def chat_text(self, prompt: str) -> str:
        return await self._chat([{"role": "user", "content": prompt}])

    async def chat_vision(self, prompt: str, image_b64: str) -> str:
        return await self._chat([{"role": "user", "content": prompt, "images": [image_b64]}])
