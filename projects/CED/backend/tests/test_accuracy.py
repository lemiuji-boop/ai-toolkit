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

"""Проверка порогов уверенности извлечения полей (CURSOR_LAUNCH)."""

from app.services.inbox_service import key_field_confidence


def test_kd_confidence_from_fields() -> None:
    data = {
        "doc_number": {"value": "АБВ.123", "confidence": 0.95},
        "name": {"value": "Корпус", "confidence": 0.88},
    }
    assert key_field_confidence(data, "kd") == 0.88


def test_ii_confidence_from_order() -> None:
    data = {"order_number": {"value": "ИИ-001", "confidence": 0.92}}
    assert key_field_confidence(data, "ii") == 0.92


def test_empty_data_returns_zero() -> None:
    assert key_field_confidence({}, "kd") == 0.0
