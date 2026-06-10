"""Контракт провайдера модели (TZ-FINAL §2). Любая модель — за этим интерфейсом."""
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class DataClass(str, Enum):
    confidential = "confidential"  # КД, обозначения, геометрия — только local
    open = "open"                  # справочные задачи без данных изделия


@dataclass(frozen=True)
class ProviderInfo:
    id: int
    name: str
    kind: str          # 'local' | 'external'
    base_url: str
    model: str
    enabled: bool
    priority: int      # меньше = выше приоритет
    api_key: str | None = None  # уже расшифрованный, только в памяти


class LLMProvider(Protocol):
    info: ProviderInfo

    async def chat_text(self, prompt: str) -> str: ...
    async def chat_vision(self, prompt: str, image_b64: str) -> str: ...
