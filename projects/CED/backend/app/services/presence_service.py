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

"""Активные сессии пользователей в Redis."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import redis.asyncio as aioredis

from app.core.config import settings

PRESENCE_TTL = 120


def _redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def touch_presence(user_id: int, login: str, role: str) -> None:
    client = _redis()
    try:
        payload = json.dumps(
            {
                "user_id": user_id,
                "login": login,
                "role": role,
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }
        )
        await client.setex(f"presence:{user_id}", PRESENCE_TTL, payload)
    finally:
        await client.aclose()


async def list_active_sessions() -> list[dict]:
    client = _redis()
    try:
        keys = await client.keys("presence:*")
        rows: list[dict] = []
        for key in keys:
            raw = await client.get(key)
            if raw:
                rows.append(json.loads(raw))
        return rows
    finally:
        await client.aclose()
