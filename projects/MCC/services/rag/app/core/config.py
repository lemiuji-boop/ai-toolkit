from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень монорепозитория MCC (services/rag/app/core → projects/MCC).
_PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Путь к persistent-хранилищу ChromaDB. Пусто → in-memory (для тестов).
    chroma_path: str = ""
    collection: str = "normatives"
    # Размерность эмбеддинга для stub-бэкенда (Ollama определяет сам).
    embed_dim: int = 768
    top_k: int = 5

    # Локальный Ollama для эмбеддингов (SEC-001: только localhost).
    ollama_url: str = "http://127.0.0.1:11434"
    embed_model: str = "nomic-embed-text"
    # auto — пробуем Ollama, иначе stub; stub — только хеширование; ollama — только Ollama.
    embed_backend: str = "auto"
    embed_timeout: float = 30.0

    # Корень проекта MCC (для путей корпуса и Chroma по умолчанию).
    project_root: str = str(_PROJECT_ROOT)
    # Автозагрузка корпуса при пустом индексе.
    auto_ingest_corpus: bool = True
    # Пути корпуса относительно project_root (через запятую в env CORPUS_PATHS).
    corpus_paths: list[str] = [
        "backend/app/data/rules.json",
        "docs/TZ.md",
        "data/rag",
    ]

    chunk_size: int = 800
    chunk_overlap: int = 120

    @field_validator("corpus_paths", mode="before")
    @classmethod
    def _parse_corpus_paths(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        return v  # type: ignore[return-value]

    def resolved_chroma_path(self) -> str:
        if self.chroma_path:
            return self.chroma_path
        return str(Path(self.project_root) / "data" / "rag" / "chroma")


settings = Settings()
