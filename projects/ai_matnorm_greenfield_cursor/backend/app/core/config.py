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

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-МАТНОРМ"
    environment: str = Field(default="local", alias="APP_ENV")
    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://ai_matnorm:ai_matnorm_dev_password@localhost:5432/ai_matnorm",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    s3_endpoint: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="minioadmin", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="ai-matnorm", alias="S3_BUCKET")
    s3_bucket_quarantine: str = Field(
        default="ai-matnorm-quarantine", alias="S3_BUCKET_QUARANTINE"
    )

    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ocr_provider: str = Field(default="tesseract", alias="OCR_PROVIDER")
    qdrant_url: str = Field(default="http://127.0.0.1:6333", alias="QDRANT_URL")
    external_llm_allowed: bool = Field(default=True, alias="EXTERNAL_LLM_ALLOWED")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_access_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(default=7, alias="JWT_REFRESH_EXPIRE_DAYS")

    admin_email: str = Field(default="admin@local.test", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="admin_change_me", alias="ADMIN_PASSWORD")

    cors_origins: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173",
        alias="CORS_ORIGINS",
    )
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")

    secrets_encryption_key: str = Field(
        default="dev-encryption-key-change-me-32bytes!!",
        alias="SECRETS_ENCRYPTION_KEY",
    )

    model_config = SettingsConfigDict(
        # .env в корне монорепо (при запуске из backend/)
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
