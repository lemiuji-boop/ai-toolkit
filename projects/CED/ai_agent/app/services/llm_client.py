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

"""Клиент Ollama для опционального уточнения полей."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from app.services.provider_resolver import ResolvedProvider, get_active_provider

logger = logging.getLogger(__name__)


def _fallback_base_url() -> str:
    return os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")


def resolve_ollama_base_url() -> str:
    """Активный провайдер из backend или OLLAMA_BASE_URL из окружения."""
    provider: ResolvedProvider = get_active_provider()
    if provider.provider_type == "local" and provider.base_url:
        return provider.base_url.rstrip("/")
    return _fallback_base_url()


def ollama_available(timeout: float = 3.0) -> bool:
    base = resolve_ollama_base_url()
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(f"{base}/api/tags")
            return response.status_code == 200
    except Exception as exc:
        logger.debug("Ollama недоступен: %s", exc)
        return False


def refine_field_with_llm(
    *,
    field_name: str,
    text_excerpt: str,
    current_value: str,
    model_name: str | None = None,
) -> dict[str, Any] | None:
    """
    Запрос к Ollama для уточнения одного поля. При ошибке возвращает None.
    """
    if not text_excerpt.strip():
        return None

    base = resolve_ollama_base_url()
    provider = get_active_provider()
    model = model_name or provider.model_name or "qwen2.5-coder"

    prompt = (
        f"Из текста конструкторского документа извлеки поле «{field_name}». "
        f"Текущее значение: {current_value or '(пусто)'}. "
        "Ответь одной строкой — только значение поля, без пояснений.\n\n"
        f"{text_excerpt[:4000]}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{base}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.warning("LLM refine failed for %s: %s", field_name, exc)
        return None

    answer = (data.get("response") or "").strip()
    if not answer or answer.lower() in {"нет", "неизвестно", "n/a"}:
        return None

    return {"value": answer[:500], "confidence": 0.75, "source": "ollama"}


def enrich_kd_fields_with_llm(
    kd_fields: dict[str, dict[str, Any]],
    full_text: str,
) -> dict[str, dict[str, Any]]:
    """Дополняет name/doc_number через Ollama, если туннель доступен."""
    if not ollama_available():
        return kd_fields

    for field in ("name", "doc_number"):
        current = kd_fields.get(field, {})
        if isinstance(current, dict) and float(current.get("confidence", 0)) >= 0.9:
            continue
        refined = refine_field_with_llm(
            field_name=field,
            text_excerpt=full_text,
            current_value=str(current.get("value", "") if isinstance(current, dict) else ""),
        )
        if refined:
            kd_fields[field] = refined
    return kd_fields
