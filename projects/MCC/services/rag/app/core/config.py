from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Путь к persistent-хранилищу ChromaDB. Пусто → in-memory (для тестов/демо).
    chroma_path: str = ""
    collection: str = "normatives"
    # Размерность детерминированного эмбеддинга (хеширование, без загрузки моделей).
    embed_dim: int = 256
    # Сколько результатов возвращать по умолчанию.
    top_k: int = 5


settings = Settings()
