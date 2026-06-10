"""Хранилище провайдеров ИИ для админ-панели (T-08, контракт §4 TZ-FINAL).

Файл data/admin/providers.json; api_key хранится только в зашифрованном виде
(Fernet через app/core/crypto.py, ключ — env SECRET_KEY). Ключи НИКОГДА
не логируются и не возвращаются в открытом виде (SEC-002/003).

Маршрутизация (FR-081): confidential-вызовы используют ТОЛЬКО kind='local';
внешние провайдеры участвуют в выборе для open-задач лишь при явном
ALLOW_EXTERNAL_PROVIDERS=1 (SEC-001 — по умолчанию исходящих вызовов нет).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any, TypedDict

from app.core import crypto
from app.core.config import settings
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.base import LLMProvider, ProviderInfo
from app.services.llm.ollama import OllamaProvider
from app.services.llm.openai_compat import OpenAICompatProvider

_lock = Lock()

# Пресеты провайдеров: kind и base_url по умолчанию. Модель указывает пользователь.
PRESETS: dict[str, dict[str, str]] = {
    "ollama": {"kind": "local", "base_url": "http://localhost:11434", "model": ""},
    "claude": {"kind": "external", "base_url": "https://api.anthropic.com", "model": ""},
    "openai": {"kind": "external", "base_url": "https://api.openai.com", "model": ""},
    "deepseek": {"kind": "external", "base_url": "https://api.deepseek.com", "model": ""},
    "mimo": {"kind": "external", "base_url": "https://api.xiaomimimo.com", "model": ""},
    "kimi": {"kind": "external", "base_url": "https://api.moonshot.ai", "model": ""},
}


class ProviderRecord(TypedDict):
    """Запись провайдера на диске (api_key — только зашифрованный)."""

    id: int
    name: str
    kind: str  # 'local' | 'external'
    base_url: str
    model: str
    api_key_encrypted: str | None
    enabled: bool
    priority: int
    created_at: str


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _store_path() -> Path:
    override = os.environ.get("MATNORM_PROVIDERS_PATH")
    if override:
        return Path(override)
    return _project_root() / "data" / "admin" / "providers.json"


def _load() -> list[ProviderRecord]:
    path = _store_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [rec for rec in data if isinstance(rec, dict) and "id" in rec]  # type: ignore[misc]


def _save(records: list[ProviderRecord]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _masked(record: ProviderRecord) -> dict[str, Any]:
    """Публичное представление: ключ маскируется, шифртекст не отдаётся."""
    has_key = bool(record.get("api_key_encrypted"))
    masked: str | None = None
    if has_key:
        try:
            masked = crypto.mask_key(crypto.decrypt_key(record["api_key_encrypted"] or ""))
        except Exception:
            # Ключ нерасшифровываем (сменился SECRET_KEY) — показываем факт наличия.
            masked = "••••????"
    return {
        "id": record["id"],
        "name": record["name"],
        "kind": record["kind"],
        "base_url": record["base_url"],
        "model": record["model"],
        "api_key_masked": masked,
        "has_api_key": has_key,
        "enabled": record["enabled"],
        "priority": record["priority"],
        "created_at": record["created_at"],
    }


def list_records() -> list[dict[str, Any]]:
    """Список провайдеров с маскированными ключами (для GET API)."""
    with _lock:
        return [_masked(r) for r in _load()]


def get_record(provider_id: int) -> ProviderRecord | None:
    with _lock:
        for rec in _load():
            if rec["id"] == provider_id:
                return rec
    return None


def create_record(
    *,
    name: str,
    kind: str,
    base_url: str,
    model: str,
    api_key: str | None,
    enabled: bool = True,
    priority: int = 100,
) -> dict[str, Any]:
    """Создать провайдера; api_key шифруется до записи на диск."""
    with _lock:
        records = _load()
        if any(r["name"] == name for r in records):
            raise ValueError(f"Провайдер с именем '{name}' уже существует")
        new_id = max((r["id"] for r in records), default=0) + 1
        rec: ProviderRecord = {
            "id": new_id,
            "name": name,
            "kind": kind,
            "base_url": base_url.rstrip("/"),
            "model": model,
            "api_key_encrypted": crypto.encrypt_key(api_key) if api_key else None,
            "enabled": enabled,
            "priority": priority,
            "created_at": datetime.now(UTC).isoformat(),
        }
        records.append(rec)
        _save(records)
        return _masked(rec)


def delete_record(provider_id: int) -> bool:
    """Удалить провайдера; True — если запись существовала."""
    with _lock:
        records = _load()
        remaining = [r for r in records if r["id"] != provider_id]
        if len(remaining) == len(records):
            return False
        _save(remaining)
        return True


def _to_provider(record: ProviderRecord) -> LLMProvider:
    """Построить runtime-провайдера; ключ расшифровывается только в память."""
    api_key: str | None = None
    if record.get("api_key_encrypted"):
        api_key = crypto.decrypt_key(record["api_key_encrypted"] or "")
    info = ProviderInfo(
        id=record["id"],
        name=record["name"],
        kind=record["kind"],
        base_url=record["base_url"],
        model=record["model"],
        enabled=record["enabled"],
        priority=record["priority"],
        api_key=api_key,
    )
    if record["kind"] == "local":
        return OllamaProvider(info, timeout=settings.inference_timeout)
    # Anthropic (Claude) использует собственный Messages API; остальные внешние
    # (OpenAI/DeepSeek/MiMo/Kimi) — OpenAI-совместимый /v1/chat/completions.
    if "anthropic" in record["base_url"].lower():
        return AnthropicProvider(info, timeout=settings.inference_timeout)
    return OpenAICompatProvider(info, timeout=settings.inference_timeout)


def runtime_provider(record: ProviderRecord) -> LLMProvider:
    """Публичная обёртка для разовых проб (test-connection в админке)."""
    return _to_provider(record)


def build_providers() -> list[LLMProvider]:
    """Активные провайдеры для router.choose.

    SEC-001: внешние (kind='external') включаются в маршрутизацию только при
    ALLOW_EXTERNAL_PROVIDERS=1. Confidential-гард остаётся в router.choose.
    """
    with _lock:
        records = _load()
    providers: list[LLMProvider] = []
    for rec in records:
        if not rec["enabled"]:
            continue
        if rec["kind"] == "external" and not settings.allow_external_providers:
            continue
        providers.append(_to_provider(rec))
    return providers
