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

"""Извлечение полей штампа КД (ГОСТ 2.104)."""

import re

from app.pipeline.extractor import extract_text
from app.pipeline.stamp_parser import extract_from_stamp, find_stamp_region


DOC_NUMBER_RE = re.compile(r"\b[А-ЯЁ]{4}\.\d{6}\.\d{3}\b")
PRODUCT_RE = re.compile(r"(?:изделие|И-)\s*№?\s*([A-ZА-Я0-9\-]+)", re.IGNORECASE)


def extract_kd_stamp(pdf_path: str) -> dict[str, dict[str, str | float]]:
    text = extract_text(pdf_path)
    _ = find_stamp_region(pdf_path)
    stamp_fields = extract_from_stamp(text)

    doc_match = DOC_NUMBER_RE.search(text)
    doc_number = stamp_fields.get("doc_number") or (doc_match.group(0) if doc_match else "")

    product_match = PRODUCT_RE.search(text)
    product = product_match.group(1) if product_match else ""

    version = stamp_fields.get("version_index", "")

    return {
        "doc_number": {"value": doc_number, "confidence": 0.95 if doc_number else 0.0},
        "name": {"value": "", "confidence": 0.5},
        "product_number": {"value": product, "confidence": 0.8 if product else 0.0},
        "version_index": {"value": version, "confidence": 0.9 if version else 0.0},
        "release_date": {
            "value": stamp_fields.get("release_date", ""),
            "confidence": 0.85 if stamp_fields.get("release_date") else 0.0,
        },
    }
