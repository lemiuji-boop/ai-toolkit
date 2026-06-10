"""Структурированный вызов модели (TZ-FINAL §2.1): JSON-схема в промпте,
Pydantic-валидация, ровно один repair-повтор, затем ошибка с сырым ответом.
Ничего не выдумывается и не подставляется."""
import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.services.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)

_REPAIR = (
    "Предыдущий ответ не соответствовал схеме. Верни СТРОГО валидный JSON по схеме, "
    "без пояснений и markdown. Нечитаемые/неизвестные поля — null. Схема: {schema}"
)


class StructuredCallError(RuntimeError):
    def __init__(self, message: str, raw: str):
        super().__init__(message)
        self.raw = raw  # сырой ответ сохраняется в лог задания, не подменяется


def _schema_prompt(prompt: str, model_cls: type[BaseModel]) -> str:
    schema = json.dumps(model_cls.model_json_schema(), ensure_ascii=False)
    return f"{prompt}\n\nОтветь строго валидным JSON по схеме (без markdown): {schema}"


def _parse(raw: str, model_cls: type[T]) -> T:
    return model_cls.model_validate_json(raw)


async def call_structured(
    provider: LLMProvider,
    prompt: str,
    model_cls: type[T],
    image_b64: str | None = None,
) -> T:
    full = _schema_prompt(prompt, model_cls)

    async def _ask(p: str) -> str:
        if image_b64 is not None:
            return await provider.chat_vision(p, image_b64)
        return await provider.chat_text(p)

    raw = await _ask(full)
    try:
        return _parse(raw, model_cls)
    except (ValidationError, ValueError):
        pass
    # ровно один repair-повтор
    schema = json.dumps(model_cls.model_json_schema(), ensure_ascii=False)
    raw2 = await _ask(_REPAIR.format(schema=schema))
    try:
        return _parse(raw2, model_cls)
    except (ValidationError, ValueError) as e:
        raise StructuredCallError(f"model response failed schema after repair: {e}", raw=raw2) from e
