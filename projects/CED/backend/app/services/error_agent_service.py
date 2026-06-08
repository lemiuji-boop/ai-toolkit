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

"""Анализ ошибок обработки КД/ИИ и уведомление администраторов."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_message import MessageSeverity, SystemMessage


def analyze_processing_error(
    *,
    context: str,
    error_text: str,
    file_path: str | None = None,
    doc_kind: str = "kd",
) -> tuple[bool, str, str]:
    """
    Возвращает (можно_исправить_автоматически, краткий_вывод, рекомендация).
  """
    low = error_text.lower()
    if "connection" in low or "timeout" in low or "ollama" in low:
        return False, "Недоступен ИИ-провайдер", "Проверьте Ollama/сеть в Настройки → ИИ-провайдеры"
    if "no such file" in low or "file_not_found" in low:
        return False, "Файл недоступен на сервере", "Проверьте UNC-корень каталога и права READ_WRITE"
    if "confidence" in low or "needs_review" in low:
        return True, "Низкая уверенность OCR", "Повторите анализ или разберите вручную в INBOX"
    if doc_kind == "ii" and "order_number" in low:
        return False, "Не распознан номер ИИ", "Загрузите скан лучшего качества или введите номер вручную"
    return False, f"Ошибка при {context}", error_text[:500]


async def notify_staff(
    db: AsyncSession,
    *,
    title: str,
    body: str,
    severity: MessageSeverity = MessageSeverity.error,
    source: str = "error_agent",
) -> SystemMessage:
    row = SystemMessage(
        title=title,
        body=body,
        severity=severity,
        target_roles="admin,moderator",
        source=source,
    )
    db.add(row)
    await db.flush()
    return row


async def handle_processing_failure(
    db: AsyncSession,
    *,
    context: str,
    error_text: str,
    file_path: str | None = None,
    doc_kind: str = "kd",
) -> dict:
    auto_fix, summary, hint = analyze_processing_error(
        context=context, error_text=error_text, file_path=file_path, doc_kind=doc_kind
    )
    body = f"{summary}\n\nВероятная причина: {hint}\n\nТехнически: {error_text[:800]}"
    if file_path:
        body += f"\n\nФайл: {file_path}"
    if not auto_fix:
        await notify_staff(
            db,
            title=f"Ошибка обработки ({doc_kind.upper()})",
            body=body,
            severity=MessageSeverity.error,
        )
    return {"auto_fixable": auto_fix, "summary": summary, "hint": hint}
