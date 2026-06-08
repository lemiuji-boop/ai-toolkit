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

import json
import uuid
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AiProvider, AiRequest


class LlmRequest(BaseModel):
    task_type: str
    prompt: str
    schema_model: type[BaseModel] | None = None


class LlmResponse(BaseModel):
    content: str
    parsed: dict[str, Any] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    provider_name: str = ""


class LlmProvider(ABC):
    @abstractmethod
    async def chat(self, request: LlmRequest) -> LlmResponse: ...


class MockLlmProvider(LlmProvider):
    async def chat(self, request: LlmRequest) -> LlmResponse:
        default = {"document_type": "part_drawing", "confidence": 0.7}
        return LlmResponse(
            content=json.dumps(default, ensure_ascii=False),
            parsed=default,
            provider_name="mock",
        )


class OllamaProvider(LlmProvider):
    def __init__(self, base_url: str, model: str = "llama3.2") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(self, request: LlmRequest) -> LlmResponse:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": request.prompt}],
                    "stream": False,
                    "format": "json",
                },
            )
            r.raise_for_status()
            data = r.json()
            content = data.get("message", {}).get("content", "{}")
        parsed = json.loads(content) if content else {}
        if request.schema_model:
            parsed = request.schema_model.model_validate(parsed).model_dump()
        return LlmResponse(
            content=content,
            parsed=parsed,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            provider_name="ollama",
        )


class OpenAICompatibleProvider(LlmProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def chat(self, request: LlmRequest) -> LlmResponse:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": request.prompt}],
                    "response_format": {"type": "json_object"},
                },
            )
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if request.schema_model:
            parsed = request.schema_model.model_validate(parsed).model_dump()
        usage = data.get("usage", {})
        return LlmResponse(
            content=content,
            parsed=parsed,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            provider_name="openai_compatible",
        )


class LlmRouter:
    def __init__(self, providers: list[LlmProvider]) -> None:
        self.providers = providers

    async def run(
        self,
        request: LlmRequest,
        db: AsyncSession | None = None,
        provider_id: uuid.UUID | None = None,
    ) -> LlmResponse:
        last_error: Exception | None = None
        for provider in self.providers:
            pid = provider_id
            inner = provider
            if hasattr(provider, "provider_id"):
                pid = provider.provider_id  # type: ignore[attr-defined]
                inner = provider.inner  # type: ignore[attr-defined]
            try:
                resp = await inner.chat(request)
                if db is not None:
                    db.add(
                        AiRequest(
                            id=uuid.uuid4(),
                            provider_id=pid,
                            task_type=request.task_type,
                            model_name=resp.provider_name,
                            prompt_tokens=resp.prompt_tokens,
                            completion_tokens=resp.completion_tokens,
                            status="ok",
                        )
                    )
                return resp
            except (httpx.HTTPError, ValidationError, json.JSONDecodeError, RuntimeError) as exc:
                last_error = exc
                if db is not None:
                    db.add(
                        AiRequest(
                            id=uuid.uuid4(),
                            provider_id=pid,
                            task_type=request.task_type,
                            model_name=getattr(inner, "__class__", type(inner)).__name__,
                            status="error",
                            error_message=str(exc),
                        )
                    )
        raise RuntimeError(f"Все провайдеры недоступны: {last_error}")


def build_default_router() -> LlmRouter:
    return LlmRouter(
        [
            OllamaProvider(settings.ollama_base_url),
            MockLlmProvider(),
        ]
    )
