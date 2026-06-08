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

"""Извлечение таблиц и layout JSON (v1)."""
import uuid
from typing import Any

from app.db.models import SpecRow


def extract_tables_from_text(
    document_id: uuid.UUID, text: str, page: int = 1
) -> list[SpecRow]:
    """Простое извлечение строк спецификации из текста (позиция + обозначение)."""
    rows: list[SpecRow] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            rows.append(
                SpecRow(
                    id=uuid.uuid4(),
                    document_id=document_id,
                    position=parts[0],
                    designation=parts[1] if len(parts) > 1 else None,
                    name=" ".join(parts[2:]) if len(parts) > 2 else None,
                    quantity=1.0,
                    confidence=0.7,
                    source_page=page,
                )
            )
    return rows


def table_to_layout_json(table_id: str, page: int, rows: list[list[str]]) -> dict[str, Any]:
    return {
        "table_id": table_id,
        "source_page": page,
        "rows": [{"cells": [{"text": c} for c in row]} for row in rows],
        "confidence": 0.75,
        "method": "text_parse",
    }
