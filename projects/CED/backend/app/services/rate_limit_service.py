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

"""Ограничение частоты запросов (Redis)."""

from __future__ import annotations

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.core.config import settings


def _redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def check_login_allowed(client_key: str) -> None:
    """Проверка блокировки без увеличения счётчика."""
    key = f"login_attempts:{client_key}"
    client = _redis()
    try:
        raw = await client.get(key)
        if raw is not None and int(raw) >= settings.login_rate_limit_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Слишком много попыток входа. Повторите позже.",
            )
    finally:
        await client.aclose()


async def register_login_failure(client_key: str) -> None:
    key = f"login_attempts:{client_key}"
    client = _redis()
    try:
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, settings.login_rate_limit_window_seconds)
    finally:
        await client.aclose()


async def reset_login_rate_limit(client_key: str) -> None:
    client = _redis()
    try:
        await client.delete(f"login_attempts:{client_key}")
    finally:
        await client.aclose()
