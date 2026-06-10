"""Тесты внешних провайдеров (egress разрешён решением пользователя 2026-06-10).

Сеть мокается (httpx.AsyncClient подменяется); проверяется:
- OpenAI-совместимый путь (openai/deepseek/mimo/kimi): URL, Bearer-заголовок, тело;
- Anthropic (claude): /v1/messages, x-api-key, разбор content-блоков;
- выбор класса провайдера по base_url в providers_store;
- маршрутизация при ALLOW_EXTERNAL_PROVIDERS=1: open → external допустим,
  confidential → по-прежнему только kind=local (FR-081).
"""
import json

import httpx
import pytest

from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.base import DataClass, ProviderInfo
from app.services.llm.openai_compat import OpenAICompatProvider
from app.services.llm.router import choose


def _info(base_url: str, kind: str = "external", **kw) -> ProviderInfo:
    return ProviderInfo(
        id=kw.get("id", 1), name=kw.get("name", "ext"), kind=kind,
        base_url=base_url, model=kw.get("model", "m"),
        enabled=True, priority=kw.get("priority", 100),
        api_key=kw.get("api_key"),
    )


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def _fake_client(captured: dict, payload: dict):
    """Подмена httpx.AsyncClient: фиксирует запрос, отдаёт payload без сети."""

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["timeout"] = kwargs.get("timeout")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc) -> bool:
            return False

        async def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = headers or {}
            captured["json"] = json or {}
            return _FakeResponse(payload)

    return _FakeAsyncClient


@pytest.mark.asyncio
async def test_openai_compat_call(monkeypatch):
    captured: dict = {}
    payload = {"choices": [{"message": {"content": '{"ok": true}'}}]}
    monkeypatch.setattr(httpx, "AsyncClient", _fake_client(captured, payload))

    p = OpenAICompatProvider(
        _info("https://api.deepseek.com", api_key="sk-test-key-9999"), timeout=33.0,
    )
    out = await p.chat_text("привет")

    assert out == '{"ok": true}'
    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-test-key-9999"
    assert captured["timeout"] == 33.0
    assert captured["json"]["model"] == "m"


@pytest.mark.asyncio
async def test_anthropic_call(monkeypatch):
    captured: dict = {}
    payload = {"content": [{"type": "text", "text": '{"ok": 1}'}]}
    monkeypatch.setattr(httpx, "AsyncClient", _fake_client(captured, payload))

    p = AnthropicProvider(
        _info("https://api.anthropic.com", api_key="sk-ant-key-1234"), timeout=44.0,
    )
    out = await p.chat_text("привет")

    assert out == '{"ok": 1}'
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "sk-ant-key-1234"
    assert "Authorization" not in captured["headers"]
    assert captured["json"]["max_tokens"] > 0
    # Ключ не утекает в тело запроса.
    assert "sk-ant-key-1234" not in json.dumps(captured["json"])


def test_store_builds_anthropic_for_claude(tmp_path, monkeypatch):
    """providers_store выбирает AnthropicProvider по base_url anthropic."""
    monkeypatch.setenv("MATNORM_PROVIDERS_PATH", str(tmp_path / "providers.json"))
    from app.core.config import settings
    from app.services import providers_store

    monkeypatch.setattr(settings, "allow_external_providers", True)
    providers_store.create_record(
        name="claude", kind="external", base_url="https://api.anthropic.com",
        model="claude-sonnet-4", api_key="sk-ant-x", priority=1,
    )
    providers_store.create_record(
        name="deepseek", kind="external", base_url="https://api.deepseek.com",
        model="deepseek-chat", api_key="sk-d", priority=2,
    )
    built = providers_store.build_providers()
    by_name = {p.info.name: p for p in built}
    assert isinstance(by_name["claude"], AnthropicProvider)
    assert isinstance(by_name["deepseek"], OpenAICompatProvider)


def test_routing_with_egress_enabled(tmp_path, monkeypatch):
    """ALLOW_EXTERNAL_PROVIDERS=1: open может уйти на external,
    confidential — только local (граница FR-081 не зависит от флага)."""
    monkeypatch.setenv("MATNORM_PROVIDERS_PATH", str(tmp_path / "providers.json"))
    from app.core.config import settings
    from app.services import providers_store
    from app.services.llm.registry import list_providers, set_providers_fn

    monkeypatch.setattr(settings, "allow_external_providers", True)
    providers_store.create_record(
        name="ext", kind="external", base_url="https://api.openai.com",
        model="gpt", api_key="sk-x", priority=1,
    )
    providers_store.create_record(
        name="loc", kind="local", base_url="http://localhost:11434",
        model="qwen", api_key=None, priority=50,
    )
    set_providers_fn(None)  # снять мок conftest — реальный реестр
    assert choose(DataClass.open, list_providers).info.kind == "external"
    assert choose(DataClass.confidential, list_providers).info.kind == "local"
