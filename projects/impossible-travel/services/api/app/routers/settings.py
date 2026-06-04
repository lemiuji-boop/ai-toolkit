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

"""Настройки."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import SettingsResponse, SettingsUpdate

router = APIRouter()

_settings = get_settings()


@router.get("", response_model=SettingsResponse)
async def get_settings_endpoint() -> SettingsResponse:
    """Публичные настройки."""
    return SettingsResponse(
        mock_generation=_settings.mock_generation,
        app_env=_settings.app_env,
        max_daily_generation_cost_usd=_settings.max_daily_generation_cost_usd,
    )


@router.patch("", response_model=SettingsResponse)
async def patch_settings(data: SettingsUpdate) -> SettingsResponse:
    """Обновление настроек (in-memory для MVP)."""
    global _settings
    if data.mock_generation is not None:
        _settings.mock_generation = data.mock_generation
    return SettingsResponse(
        mock_generation=_settings.mock_generation,
        app_env=_settings.app_env,
        max_daily_generation_cost_usd=_settings.max_daily_generation_cost_usd,
    )
