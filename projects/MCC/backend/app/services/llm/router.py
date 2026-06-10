"""Маршрутизатор по классу данных — единственная точка выбора провайдера
(TZ-FINAL §2.2, FR-081). confidential → только kind='local'."""
from collections.abc import Callable, Sequence

from app.services.llm.base import DataClass, LLMProvider

# Поставщик списка провайдеров внедряется (реестр из БД в T-08).
ProvidersFn = Callable[[], Sequence[LLMProvider]]


class NoLocalProviderError(RuntimeError):
    """Нет локального провайдера для confidential-вызова → API отдаёт 503 NO_LOCAL_PROVIDER."""
    code = "NO_LOCAL_PROVIDER"


class NoProviderError(RuntimeError):
    code = "NO_PROVIDER"


def choose(data_class: DataClass, providers_fn: ProvidersFn) -> LLMProvider:
    enabled = sorted(
        (p for p in providers_fn() if p.info.enabled),
        key=lambda p: p.info.priority,
    )
    if data_class is DataClass.confidential:
        local = [p for p in enabled if p.info.kind == "local"]
        if not local:
            raise NoLocalProviderError("confidential call requires a local provider")
        return local[0]
    if not enabled:
        raise NoProviderError("no enabled providers")
    return enabled[0]
