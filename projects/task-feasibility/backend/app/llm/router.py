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

"""Маршрутизация L1–L4 к провайдерам."""

import re

import httpx

from app.config import ComplexityLevel, get_settings
from app.llm.providers.base import ChatMessage, LLMResponse
from app.llm.providers.ollama import OllamaProvider
from app.llm.providers.openai_compat import OpenAICompatibleProvider
from app.schemas.safety import SafetyShieldPayload


class LLMRouter:
    """Выбор провайдера и стратегии по уровню сложности."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._ollama = OllamaProvider()
        self._cloud = OpenAICompatibleProvider()
        self._warnings: list[str] = []

    @property
    def warnings(self) -> list[str]:
        """Предупреждения последнего вызова (fallback и т.д.)."""
        return list(self._warnings)

    def prune_context(self, text: str) -> str:
        """L2: убираем комментарии и лишние пробелы."""
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            lines.append(re.sub(r"\s+", " ", line).strip())
        return "\n".join(l for l in lines if l)

    async def complete(
        self,
        level: ComplexityLevel,
        messages: list[ChatMessage],
        *,
        encryption_required: bool = False,
        use_pruning: bool = False,
    ) -> LLMResponse:
        """
        Вызов модели с учётом уровня.

        L1 → Ollama (fallback cloud с warning)
        L2–L4 → cloud; financial → только Ollama
        """
        self._warnings = []
        settings = self._settings
        max_tokens = settings.get_max_tokens(level)
        model = settings.get_model(level)

        if use_pruning and messages:
            last = messages[-1]
            if last.role == "user":
                messages = messages[:-1] + [
                    ChatMessage(role="user", content=self.prune_context(last.content))
                ]

        # Финансовые данные — строго локально
        force_local = encryption_required or level == "L1"

        if force_local:
            if await self._ollama.is_available():
                try:
                    return await self._ollama.chat(messages, model, max_tokens)
                except (httpx.HTTPError, OSError) as exc:
                    self._warnings.append(f"Ошибка Ollama: {exc}")
            self._warnings.append(
                "Ollama недоступен; для L1/финансовых данных требуется локальный узел."
            )
            if await self._cloud.is_available():
                self._warnings.append(
                    "ВНИМАНИЕ: fallback на облако — не рекомендуется для чувствительных данных."
                )
                return await self._cloud.chat(messages, model, max_tokens)
            raise RuntimeError("Нет доступных LLM-провайдеров")

        if await self._cloud.is_available():
            try:
                return await self._cloud.chat(messages, model, max_tokens)
            except (httpx.HTTPError, OSError) as exc:
                self._warnings.append(f"Ошибка облачного провайдера: {exc}")

        if await self._ollama.is_available():
            self._warnings.append("Облако недоступно; используется Ollama.")
            try:
                return await self._ollama.chat(messages, model, max_tokens)
            except (httpx.HTTPError, OSError) as exc:
                self._warnings.append(f"Ошибка Ollama: {exc}")

        raise RuntimeError("Нет доступных LLM-провайдеров")

    async def health(self) -> dict[str, bool | list[str]]:
        """Статус провайдеров."""
        return {
            "ollama": await self._ollama.is_available(),
            "cloud": await self._cloud.is_available(),
            "ollama_models": await self._ollama.list_models(),
        }
