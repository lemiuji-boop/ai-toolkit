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

"""Регулярные выражения и эвристики для детекции чувствительных данных."""

import math
import re
from collections.abc import Callable
from re import Pattern

# Credentials & IDs — hard block
CREDENTIAL_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (
        "credentials:api_key",
        re.compile(
            r"(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[=:]\s*['\"]?"
            r"[A-Za-z0-9_\-]{16,}",
        ),
    ),
    (
        "credentials:bearer",
        re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    ),
    (
        "credentials:password",
        re.compile(
            r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{6,}",
        ),
    ),
    (
        "credentials:private_key",
        re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    ),
    (
        "credentials:gov_id",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-подобный
    ),
    (
        "credentials:passport",
        re.compile(r"(?i)passport\s*(?:no\.?|number)?\s*[:#]?\s*[A-Z0-9]{6,12}"),
    ),
]

# Financial — local only
FINANCIAL_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (
        "financial:card",
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    ),
    (
        "financial:iban",
        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    ),
    (
        "financial:bank",
        re.compile(
            r"(?i)(bank\s+account|routing\s+number|transaction\s+history|credit\s+card)",
        ),
    ),
]

# Medical — mask from cloud
MEDICAL_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (
        "medical:condition",
        re.compile(
            r"(?i)\b(diagnosed with|medical condition|mental health|pregnancy|"
            r"disability|prescription)\b",
        ),
    ),
]

# Identity — strip unless explicit consent (MVP: always strip)
IDENTITY_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (
        "identity:demographics",
        re.compile(
            r"(?i)\b(race|religion|sexual orientation|political affiliation|"
            r"national origin)\b",
        ),
    ),
]

MASK_PLACEHOLDERS: dict[str, str] = {
    "financial:card": "[MASKED_CARD]",
    "financial:iban": "[MASKED_IBAN]",
    "medical:condition": "[MASKED_MEDICAL]",
    "identity:demographics": "[MASKED_IDENTITY]",
}


def shannon_entropy(text: str) -> float:
    """Энтропия Шеннона для эвристики случайных секретов."""
    if not text:
        return 0.0
    freq: dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def detect_high_entropy_secret(text: str, min_length: int = 32) -> list[str]:
    """Поиск высокоэнтропийных токенов (подозрение на API key)."""
    violations: list[str] = []
    for token in re.findall(r"[A-Za-z0-9_\-]{32,}", text):
        if shannon_entropy(token) >= 4.2:
            violations.append("credentials:high_entropy_token")
            break
    return violations


def scan_patterns(
    text: str,
    patterns: list[tuple[str, Pattern[str]]],
) -> list[str]:
    """Сканирование текста по списку паттернов."""
    found: list[str] = []
    for label, pattern in patterns:
        if pattern.search(text):
            found.append(label)
    return found


def mask_text(
    text: str,
    patterns: list[tuple[str, Pattern[str]]],
    placeholders: dict[str, str] | None = None,
) -> str:
    """Замена совпадений на плейсхолдеры."""
    result = text
    ph = placeholders or MASK_PLACEHOLDERS
    for label, pattern in patterns:
        placeholder = ph.get(label, "[MASKED]")
        result = pattern.sub(placeholder, result)
    return result
