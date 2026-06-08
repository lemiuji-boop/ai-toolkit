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

"""Проверка Ollama и учёт токенов (оценка)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from sqlalchemy.orm import Session

from app.db.models import OllamaModel, SystemSetting, TokenUsage
from app.services.activity import log_activity


def get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.get(SystemSetting, key)
    return row.value if row else default


def check_ollama_usage(db: Session, *, admin_username: str = "admin") -> dict:
    """Запрос к Ollama и запись оценки расхода токенов в журнал."""
    base = get_setting(db, "ollama_base_url", "http://127.0.0.1:11434").rstrip("/")
    model = get_setting(db, "active_ollama_model", "")
    if not model:
        active = db.query(OllamaModel).filter(OllamaModel.is_active.is_(True)).first()
        model = active.model_name if active else "llama3.2:3b"

    prompt = "Ответь одним словом: ок"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    url = f"{base}/api/generate"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        log_activity(db, action="ollama_check_failed", detail=str(exc), username=admin_username)
        return {"ok": False, "error": str(exc), "model": model}

    response_text = data.get("response", "")
    # Ollama отдаёт eval_count — завершённые токены; prompt — оценка по длине prompt
    completion = int(data.get("eval_count") or len(response_text.split()))
    prompt_tokens = int(data.get("prompt_eval_count") or max(1, len(prompt.split())))
    total = prompt_tokens + completion

    db.add(
        TokenUsage(
            model_name=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion,
            total_tokens=total,
            source="admin_check",
        )
    )
    log_activity(
        db,
        action="ollama_check",
        detail=f"{model}: {total} токенов (≈)",
        username=admin_username,
    )
    db.commit()
    return {
        "ok": True,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion,
        "total_tokens": total,
        "response_preview": response_text[:120],
    }


def list_ollama_tags(db: Session) -> list[str]:
    """Список моделей с сервера Ollama."""
    base = get_setting(db, "ollama_base_url", "http://127.0.0.1:11434").rstrip("/")
    url = f"{base}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
