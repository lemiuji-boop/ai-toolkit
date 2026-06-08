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

"""Разбор формы извещения об изменении (ГОСТ 2.503)."""

import re
from typing import Any

from app.pipeline.extractor import extract_text

ORDER_RE = re.compile(r"(?:ИИ|Извещение)\s*№?\s*([A-ZА-Я0-9\-\.]+)", re.IGNORECASE)
DOC_RE = re.compile(r"\b[А-ЯЁ]{4}\.\d{6}\.\d{3}\b")
DATE_RE = re.compile(r"\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2}")
PRODUCT_IMPL_RE = re.compile(r"с\s+изделия\s+№?\s*([A-ZА-Я0-9\-]+)", re.IGNORECASE)

BACKLOG_MAP = {
    "израсходовать": "use",
    "доработать": "rework",
    "исправить": "fix",
    "забраковать": "scrap",
}


def classify_backlog(line: str) -> str | None:
    low = line.lower()
    for key, value in BACKLOG_MAP.items():
        if key in low:
            return value
    return None


def parse_directives_from_text(text: str) -> list[dict[str, Any]]:
    directives: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        backlog = classify_backlog(line)
        docs = DOC_RE.findall(line)
        if not backlog and not docs:
            continue

        impl_kind = "immediate"
        impl_product = None
        impl_date = None
        if PRODUCT_IMPL_RE.search(line):
            impl_kind = "from_product"
            impl_product = PRODUCT_IMPL_RE.search(line).group(1)  # type: ignore[union-attr]
        date_match = DATE_RE.search(line)
        if date_match:
            impl_kind = "from_date"
            impl_date = date_match.group(0)

        for doc_number in docs or [None]:
            directives.append(
                {
                    "affected_doc_number": doc_number,
                    "backlog_action": backlog,
                    "implementation_kind": impl_kind,
                    "implementation_product": impl_product,
                    "implementation_date": impl_date,
                    "directive_text": line.strip(),
                    "confidence": 0.75 if backlog else 0.5,
                }
            )
    return directives


def extract_ii_form(pdf_path: str) -> dict[str, Any]:
    text = extract_text(pdf_path)
    order_match = ORDER_RE.search(text)
    order_number = order_match.group(1) if order_match else ""

    directives = parse_directives_from_text(text)
    if not directives:
        directives = [
            {
                "affected_doc_number": None,
                "backlog_action": None,
                "implementation_kind": "immediate",
                "implementation_product": None,
                "implementation_date": None,
                "directive_text": text[:500],
                "confidence": 0.3,
            }
        ]

    return {
        "order_number": {"value": order_number, "confidence": 0.9 if order_number else 0.0},
        "directives": directives,
    }
