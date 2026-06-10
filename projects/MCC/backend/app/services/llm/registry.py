"""Реестр провайдеров: из env (каркас) или БД (T-08). Единая точка для router.choose."""
from collections.abc import Callable, Sequence

from app.core.config import settings
from app.services.llm.base import LLMProvider, ProviderInfo
from app.services.llm.ollama import OllamaProvider

ProvidersFn = Callable[[], Sequence[LLMProvider]]

_override: ProvidersFn | None = None


def set_providers_fn(fn: ProvidersFn | None) -> None:
    """Тестовый хук: подмена списка провайдеров без БД."""
    global _override
    _override = fn


def _env_default_provider() -> LLMProvider:
    """Локальный Ollama из настроек — до появления CRUD провайдеров в БД."""
    info = ProviderInfo(
        id=0,
        name="env-ollama",
        kind="local",
        base_url=settings.inference_url,
        model=settings.vlm_model,
        enabled=True,
        priority=10,
    )
    return OllamaProvider(info, timeout=settings.inference_timeout)


def list_providers() -> list[LLMProvider]:
    """Провайдеры для router.choose: тест-хук → хранилище админки → env-default.

    Если в data/admin/providers.json нет ни одного активного локального провайдера,
    добавляется env-Ollama — каркас остаётся работоспособным без настройки.
    """
    if _override is not None:
        return list(_override())
    # Импорт внутри функции — разрыв цикла providers_store ↔ registry.
    from app.services import providers_store

    providers: list[LLMProvider] = providers_store.build_providers()
    if not any(p.info.kind == "local" for p in providers):
        providers.append(_env_default_provider())
    return providers
