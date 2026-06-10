"""Фикстуры: in-memory хранилище и stub-эмбеддинги (без Ollama/Chroma на диске)."""
import os

# До импорта app — изолированное окружение тестов.
os.environ["CHROMA_PATH"] = "memory"
os.environ["EMBED_BACKEND"] = "stub"
os.environ["AUTO_INGEST_CORPUS"] = "false"

from app.corpus import bootstrap_index

# TestClient на уровне модуля не всегда прогоняет lifespan — сид явно.
bootstrap_index()
