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

"""Конфигурация приложения через переменные окружения."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ComplexityLevel = Literal["L1", "L2", "L3", "L4"]


class Settings(BaseSettings):
    """Настройки MATFES из .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MATFES"
    debug: bool = False
    api_prefix: str = "/api/v1"

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    cloud_api_base: str = Field(
        default="https://api.openai.com/v1",
        alias="CLOUD_API_BASE",
    )
    cloud_api_key: str = Field(default="", alias="CLOUD_API_KEY")

    model_l1: str = Field(default="qwen2.5-coder:7b", alias="DEFAULT_MODEL_L1")
    model_l2: str = Field(default="gpt-4o-mini", alias="DEFAULT_MODEL_L2")
    model_l3: str = Field(default="gpt-4o", alias="DEFAULT_MODEL_L3")
    model_l4: str = Field(default="gpt-4o", alias="DEFAULT_MODEL_L4")

    max_tokens_l1: int = Field(default=500, alias="MAX_TOKENS_L1")
    max_tokens_l2: int = Field(default=4096, alias="MAX_TOKENS_L2")
    max_tokens_l3: int = Field(default=8192, alias="MAX_TOKENS_L3")
    max_tokens_l4: int = Field(default=16384, alias="MAX_TOKENS_L4")

    feasibility_threshold: float = Field(default=0.7, alias="FEASIBILITY_THRESHOLD")

    # Цены за 1M токенов (USD), базовая линия 2026
    price_input_per_million: float = Field(default=2.5, alias="PRICE_INPUT_PER_MILLION")
    price_output_per_million: float = Field(default=10.0, alias="PRICE_OUTPUT_PER_MILLION")
    price_cached_input_per_million: float = Field(
        default=1.25,
        alias="PRICE_CACHED_INPUT_PER_MILLION",
    )

    # Коэффициенты оценки токенов (ТЗ §5)
    alpha_tokens_per_context_line: float = 35.0
    beta_tokens_per_output_line: float = 40.0

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    def get_max_tokens(self, level: ComplexityLevel) -> int:
        """Лимит выходных токенов по уровню сложности."""
        mapping: dict[ComplexityLevel, int] = {
            "L1": self.max_tokens_l1,
            "L2": self.max_tokens_l2,
            "L3": self.max_tokens_l3,
            "L4": self.max_tokens_l4,
        }
        return mapping[level]

    def get_model(self, level: ComplexityLevel) -> str:
        """Имя модели по уровню сложности."""
        mapping: dict[ComplexityLevel, str] = {
            "L1": self.model_l1,
            "L2": self.model_l2,
            "L3": self.model_l3,
            "L4": self.model_l4,
        }
        return mapping[level]

    @property
    def cors_origin_list(self) -> list[str]:
        """Список разрешённых CORS origin."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Синглтон настроек."""
    return Settings()
