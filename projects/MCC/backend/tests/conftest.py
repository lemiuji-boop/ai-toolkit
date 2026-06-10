"""Общие фикстуры: мок локального LLM-провайдера для герметичных тестов."""
import json
import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret")

from app.services.llm.base import ProviderInfo
from app.services.llm.registry import set_providers_fn


class _MockVisionProvider:
    """Имитация локального провайдера с детерминированным JSON-ответом."""

    def __init__(self, payload: dict | None = None) -> None:
        self.info = ProviderInfo(
            id=0,
            name="mock-local",
            kind="local",
            base_url="http://mock",
            model="mock-vlm",
            enabled=True,
            priority=1,
        )
        self._payload = payload or {
            "designation": "АБВГ.001.001",
            "name": "Кронштейн",
            "material": "Д16",
            "mass_kg": 0.42,
            "dimensions_mm": {"length": 180.0, "width": 90.0, "height": 24.0},
            "confidence": {"designation": 0.9, "material": 0.85},
        }

    async def chat_text(self, prompt: str) -> str:
        return json.dumps(self._payload, ensure_ascii=False)

    async def chat_vision(self, prompt: str, image_b64: str) -> str:
        return await self.chat_text(prompt)


@pytest.fixture(autouse=True)
def _default_mock_provider():
    set_providers_fn(lambda: [_MockVisionProvider()])
    yield
    set_providers_fn(None)


@pytest.fixture(autouse=True)
def _no_external_providers(monkeypatch):
    """Герметичность: тесты не зависят от ALLOW_EXTERNAL_PROVIDERS в локальном .env.

    Тесты, которым нужен egress-флаг, включают его явно через monkeypatch.
    """
    from app.core.config import settings

    monkeypatch.setattr(settings, "allow_external_providers", False)


@pytest.fixture(autouse=True)
def _bypass_admin_auth():
    """Обход JWT-защиты /api/admin/* для функциональных тестов.

    Тесты самой аутентификации (tests/test_auth.py) снимают этот override
    фикстурой real_auth.
    """
    from app.api.auth import require_admin
    from app.main import app

    app.dependency_overrides[require_admin] = lambda: {"sub": "test", "role": "admin"}
    yield
    app.dependency_overrides.pop(require_admin, None)
