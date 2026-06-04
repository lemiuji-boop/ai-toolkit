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

"""SafetyShield — предобработка перед внешними API."""

from app.guardrails import patterns as pat
from app.schemas.safety import SafetyShieldPayload


class SafetyShield:
    """Программный guardrail-слой (ТЗ §3)."""

    def scan(self, user_input: str) -> SafetyShieldPayload:
        """
        Проверяет ввод и возвращает sanitized prompt.

        credentials → hard_block
        financial → encryption_required, только локальная обработка
        medical/identity → маскирование
        """
        violations: list[str] = []

        cred = pat.scan_patterns(user_input, pat.CREDENTIAL_PATTERNS)
        cred.extend(pat.detect_high_entropy_secret(user_input))
        violations.extend(cred)

        financial = pat.scan_patterns(user_input, pat.FINANCIAL_PATTERNS)
        medical = pat.scan_patterns(user_input, pat.MEDICAL_PATTERNS)
        identity = pat.scan_patterns(user_input, pat.IDENTITY_PATTERNS)

        hard_blocked = bool(cred)
        encryption_required = bool(financial) and not hard_blocked

        violations.extend(financial)
        violations.extend(medical)
        violations.extend(identity)

        sanitized = user_input
        if not hard_blocked:
            sanitized = pat.mask_text(sanitized, pat.FINANCIAL_PATTERNS)
            sanitized = pat.mask_text(sanitized, pat.MEDICAL_PATTERNS)
            sanitized = pat.mask_text(sanitized, pat.IDENTITY_PATTERNS)

        is_safe = not hard_blocked and not encryption_required or (
            not hard_blocked and encryption_required
        )
        # Для financial: безопасно экспортировать только после маскирования
        if encryption_required:
            is_safe = "[MASKED_CARD]" in sanitized or "[MASKED_IBAN]" in sanitized or (
                not pat.scan_patterns(sanitized, pat.FINANCIAL_PATTERNS)
            )

        return SafetyShieldPayload(
            is_safe_to_export=not hard_blocked and is_safe,
            detected_violations=list(dict.fromkeys(violations)),
            sanitized_prompt=sanitized if not hard_blocked else "",
            encryption_required=encryption_required,
            hard_blocked=hard_blocked,
        )
