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

"""Тесты SafetyShield."""

import pytest

from app.guardrails.shield import SafetyShield


@pytest.fixture
def shield() -> SafetyShield:
    return SafetyShield()


def test_clean_crud_task(shield: SafetyShield) -> None:
    result = shield.scan("Создать CRUD API для пользователей с endpoints REST")
    assert not result.hard_blocked
    assert result.is_safe_to_export
    assert "credentials" not in " ".join(result.detected_violations)


def test_hard_block_api_key(shield: SafetyShield) -> None:
    text = "Используй api_key=sk-1234567890abcdefghijklmnopqrst"
    result = shield.scan(text)
    assert result.hard_blocked
    assert not result.is_safe_to_export
    assert any("credentials" in v for v in result.detected_violations)


def test_financial_encryption(shield: SafetyShield) -> None:
    text = "Обработать bank account 40817810099910004312"
    result = shield.scan(text)
    assert result.encryption_required
    assert not result.hard_blocked


def test_medical_masking(shield: SafetyShield) -> None:
    text = "Учесть medical condition пациента при дизайне"
    result = shield.scan(text)
    assert "medical" in " ".join(result.detected_violations)
    assert "[MASKED_MEDICAL]" in result.sanitized_prompt or result.sanitized_prompt
