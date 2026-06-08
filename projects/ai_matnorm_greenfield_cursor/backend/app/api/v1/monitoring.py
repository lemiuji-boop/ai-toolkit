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

import redis.asyncio as aioredis
from fastapi import APIRouter
from rq import Worker

from app.core.config import settings
from app.db.session import check_database_connection
from app.services.storage.s3 import get_storage
from app.workers.rq_app import get_redis_connection

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


async def _redis_ok() -> bool:
    try:
        client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False


def _minio_ok() -> bool:
    try:
        get_storage()._client.head_bucket(Bucket=settings.s3_bucket)
        return True
    except Exception:
        return False


def _worker_status() -> str:
    try:
        conn = get_redis_connection()
        workers = Worker.all(connection=conn)
        if workers:
            return "ok"
        return "no_workers"
    except Exception:
        return "unavailable"


@router.get("/status")
async def monitoring_status() -> dict:
    db_ok = await check_database_connection()
    redis_ok = await _redis_ok()
    minio_ok = _minio_ok()
    worker = _worker_status()
    parts = {
        "api": "ok",
        "postgres": "ok" if db_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
        "minio": "ok" if minio_ok else "unavailable",
        "worker": worker,
    }
    status = "ok" if all(v == "ok" for k, v in parts.items() if k != "worker") else "degraded"
    return {"status": status, "components": parts}


@router.get("/health")
async def monitoring_health() -> dict:
    return await monitoring_status()
