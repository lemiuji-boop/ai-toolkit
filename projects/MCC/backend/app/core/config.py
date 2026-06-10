from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Публичный URL сервиса (TZ-FINAL §4).
    public_base_url: str = "https://matnorm.lan"
    # Ключ шифрования API-ключей провайдеров (TZ-FINAL §4).
    secret_key: str = "dev-secret-change-in-production"
    # URL БД (sqlite для тестов/разработки; postgres в compose).
    database_url: str = "sqlite+aiosqlite:///./matnorm.db"

    # SEC-001: внешние провайдеры ИИ участвуют в маршрутизации и test-connection
    # только при явном включении (по умолчанию исходящих вызовов нет).
    allow_external_providers: bool = False

    # Аутентификация админки (T-16): учётные данные администратора из env,
    # JWT подписывается SECRET_KEY (HS256), TTL в минутах.
    admin_user: str = "admin"
    admin_password: str = ""  # пустое значение → вход отключён (403 AUTH_DISABLED)
    jwt_ttl_minutes: int = 720

    # Локальный inference (LLM на Ubuntu-хосте). Без провайдера — 503, не заглушка.
    inference_url: str = "http://localhost:11434"
    vlm_model: str = "qwen2.5vl:3b"
    inference_timeout: float = 120.0

    # OCR-препроцессор (FR-002): растеризация PDF и локализация зон чертежа.
    image_dpi: int = 200          # 150–200 для пилота на 6 ГБ VRAM
    ocr_enabled: bool = True
    # Порог уверенности (FR-003): ниже него поле помечается на перепроверку.
    conf_threshold: float = 0.7

    # URL локальных сервисов для проб админ-панели (только localhost).
    backend_url: str = "http://127.0.0.1:8123"
    rag_url: str = "http://127.0.0.1:8020"
    addin_url: str = "http://127.0.0.1:3000"

    # Источники, которым разрешён CORS: надстройка Excel, админ-панель, LAN HTTPS.
    cors_origins: list[str] = [
        "https://localhost:3000",
        "http://localhost:3000",
        "http://localhost:3010",
        "http://127.0.0.1:3010",
        "http://localhost:8123",
        "http://127.0.0.1:8123",
    ]
    # Regex: подсеть 192.168.* (LAN HTTPS) и опционально trycloudflare (отладка).
    cors_origin_regex: str | None = (
        r"^https://192\.168\.[0-9]+\.[0-9]+(:[0-9]+)?$|^https://[a-z0-9-]+\.trycloudflare\.com$"
    )

    # Производство: сколько данной сборки на 1 самолёто-комплект.
    sets_per_aircraft: int = 1


settings = Settings()
