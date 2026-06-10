"""OpenAI-совместимый провайдер: vLLM, llama.cpp-server, внешние API по ключу."""
import httpx

from app.services.llm.base import ProviderInfo


class OpenAICompatProvider:
    def __init__(self, info: ProviderInfo, timeout: float = 120.0):
        self.info = info
        self._timeout = timeout

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.info.api_key:
            h["Authorization"] = f"Bearer {self.info.api_key}"
        return h

    async def _chat(self, content) -> str:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                f"{self.info.base_url.rstrip('/')}/v1/chat/completions",
                headers=self._headers(),
                json={
                    "model": self.info.model,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "user", "content": content}],
                },
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

    async def chat_text(self, prompt: str) -> str:
        return await self._chat(prompt)

    async def chat_vision(self, prompt: str, image_b64: str) -> str:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
        ]
        return await self._chat(content)
