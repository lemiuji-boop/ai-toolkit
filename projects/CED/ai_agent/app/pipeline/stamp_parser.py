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

"""Координатный поиск штампа чертежа (правый нижний угол)."""

import re

import fitz


def find_stamp_region(pdf_path: str) -> dict[str, float] | None:
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        rect = page.rect
        # Правый нижний угол — типовая зона основной надписи по ГОСТ.
        x0 = rect.width * 0.55
        y0 = rect.height * 0.75
        clip = fitz.Rect(x0, y0, rect.width, rect.height)
        text = page.get_text("text", clip=clip)
        doc.close()
        if len(text.strip()) > 20:
            return {"x_ratio": 0.55, "y_ratio": 0.75, "w_ratio": 0.45, "h_ratio": 0.25}
    except Exception:
        pass
    return {"x_ratio": 0.65, "y_ratio": 0.65, "w_ratio": 0.35, "h_ratio": 0.35}


def extract_from_stamp(text: str) -> dict[str, str]:
    patterns = {
        "doc_number": r"\b[А-ЯЁ]{4}\.\d{6}\.\d{3}\b",
        "version_index": r"(?:Верс\.?|Изм\.?)\s*([A-ZА-Я])",
        "release_date": r"(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})",
    }
    out: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            out[key] = match.group(1) if match.lastindex else match.group(0)
    return out
