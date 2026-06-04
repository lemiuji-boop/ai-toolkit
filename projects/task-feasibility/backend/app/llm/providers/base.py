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

"""Базовый интерфейс LLM-провайдера."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage:
    """Сообщение чата."""

    role: Role
    content: str


@dataclass
class LLMResponse:
    """Ответ модели."""

    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0


class LLMProvider(ABC):
    """Абстрактный провайдер."""

    name: str = "base"

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        max_tokens: int,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Асинхронный вызов chat completion."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Проверка доступности провайдера."""
