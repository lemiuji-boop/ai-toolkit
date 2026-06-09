from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Локальный inference (LLM на Ubuntu-хосте). Если недоступен — сервис
    # деградирует к детерминированной заглушке, чтобы каркас был работоспособен.
    inference_url: str = "http://localhost:11434"
    vlm_model: str = "qwen2.5vl:3b"
    inference_timeout: float = 120.0

    # OCR-препроцессор (FR-002): растеризация PDF и локализация зон чертежа.
    image_dpi: int = 200          # 150–200 для пилота на 6 ГБ VRAM
    ocr_enabled: bool = True
    # Порог уверенности (FR-003): ниже него поле помечается на перепроверку.
    conf_threshold: float = 0.7

    # Источники, которым разрешён CORS: адрес надстройки на Vercel + локальная разработка.
    cors_origins: list[str] = [
        "https://localhost:3000",
        "http://localhost:3000",
        "https://your-addin.vercel.app",
    ]

    # Производство: сколько данной сборки на 1 самолёто-комплект.
    sets_per_aircraft: int = 1


settings = Settings()
