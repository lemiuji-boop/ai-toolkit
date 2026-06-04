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

"""Application settings via pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Central configuration — all env vars go here."""

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        alias="DATABASE_URL",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    n_repeats: int = Field(default=3, alias="N_REPEATS")
    default_seed: int = Field(default=42, alias="DEFAULT_SEED")
    gpu_vram_gb: float = Field(default=6.0, alias="GPU_VRAM_GB")
    vram_safety_gb: float = Field(default=1.2, alias="VRAM_SAFETY_GB")
    judge_mode: str = Field(default="local", alias="JUDGE_MODE")
    judge_local_model: str = Field(default="qwen3:8b", alias="JUDGE_LOCAL_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    tg_bot_token: str = Field(default="", alias="TG_BOT_TOKEN")
    tg_channel_id: str = Field(default="", alias="TG_CHANNEL_ID")
    tg_admin_id: str = Field(default="", alias="TG_ADMIN_ID")
    tg_test_channel_id: str = Field(default="", alias="TG_TEST_CHANNEL_ID")
    brand_name: str = Field(default="Локальные модели на 6 ГБ", alias="BRAND_NAME")
    chart_theme: str = Field(default="dark", alias="CHART_THEME")


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
