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

"""RAG через Qdrant — индексация подтверждённых фактов."""
import hashlib
import uuid
from typing import Any

import httpx

from app.core.config import settings

COLLECTION = "ai_matnorm_facts"


def _collection_url() -> str:
    return f"{settings.qdrant_url.rstrip('/')}/collections/{COLLECTION}"


def ensure_collection() -> None:
    """Создать коллекцию при отсутствии (идемпотентно)."""
    try:
        with httpx.Client(timeout=5) as client:
            r = client.get(_collection_url())
            if r.status_code == 200:
                return
            client.put(
                _collection_url(),
                json={"vectors": {"size": 8, "distance": "Cosine"}},
            )
    except Exception:
        pass


def _embedding(text: str) -> list[float]:
    """Простой детерминированный вектор для dev (без ML-модели)."""
    h = hashlib.sha256(text.encode()).digest()
    return [((h[i % len(h)] / 255.0) - 0.5) for i in range(8)]


def index_approved_fact(fact_id: uuid.UUID, field: str, value: str, document_id: str) -> None:
    """Индексация подтверждённого факта (FR-090)."""
    ensure_collection()
    point_id = str(fact_id)
    payload = {
        "field": field,
        "value": value,
        "document_id": document_id,
        "type": "approved_fact",
    }
    vector = _embedding(f"{field}:{value}")
    try:
        with httpx.Client(timeout=5) as client:
            client.put(
                f"{_collection_url()}/points",
                json={
                    "points": [
                        {"id": point_id, "vector": vector, "payload": payload},
                    ]
                },
            )
    except Exception:
        pass


def search_similar(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Поиск похожих эталонов."""
    ensure_collection()
    try:
        with httpx.Client(timeout=5) as client:
            r = client.post(
                f"{_collection_url()}/points/search",
                json={"vector": _embedding(query), "limit": limit, "with_payload": True},
            )
            if r.status_code != 200:
                return []
            return [
                {"score": hit.get("score"), "payload": hit.get("payload")}
                for hit in r.json().get("result", [])
            ]
    except Exception:
        return []
