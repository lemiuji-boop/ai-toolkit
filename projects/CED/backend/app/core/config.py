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
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    debug: bool = True
    app_env: str = "dev"

    database_url: str = Field(default="postgresql+asyncpg://ced:ced@localhost:5432/ced")
    sync_database_url: str = Field(default="postgresql://ced:ced@localhost:5432/ced")
    redis_url: str = Field(default="redis://localhost:6379/0")

    jwt_secret_key: str = Field(default="change-me")
    jwt_refresh_secret_key: str = Field(default="change-me-refresh")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 1440

    file_storage_root: str = "/data/storage"
    catalog_root: str = Field(default="/data/catalog")
    inbox_subdir: str = "_INBOX"
    archive_subdir: str = "_ARCHIVE"
    catalog_subdir: str = "catalog"
    storage_probe_cache_minutes: int = 5
    inbox_confidence_threshold: float = 0.7

    ai_agent_base_url: str = "http://ai-agent:8001"
    ai_agent_api_key: str = "change-me-ai"
    ai_fernet_key: str = Field(default="change-me-fernet-key-32bytes!!")

    enable_inbox_watcher: bool = True

    max_upload_bytes: int = 100 * 1024 * 1024
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 900

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost"]


settings = Settings()
