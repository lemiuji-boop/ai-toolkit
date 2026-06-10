"""Первичное наполнение и автозагрузка корпуса."""
from __future__ import annotations

import logging

from app import store
from app.core.config import settings
from app.core.ingest import ingest_files
from app.core.schemas import IngestRequest
from app.seed import SEED

logger = logging.getLogger(__name__)


def bootstrap_index() -> None:
    """Сид + корпус при пустом индексе (если AUTO_INGEST_CORPUS)."""
    if store.count() > 0:
        return
    store.add(SEED)
    if not settings.auto_ingest_corpus:
        return
    req = IngestRequest(use_default_corpus=True, paths=[])
    docs, files = ingest_files(req)
    if docs:
        store.add(docs)
        logger.info("Корпус загружен: %d чанков из %d файлов", len(docs), len(files))
