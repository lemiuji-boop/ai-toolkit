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

import redis
from rq import Queue, Worker

from app.core.config import settings


def get_redis_connection() -> redis.Redis:
    return redis.from_url(settings.redis_url)


def get_queue(name: str = "default") -> Queue:
    return Queue(name, connection=get_redis_connection())


def run_worker(queues: list[str] | None = None) -> None:
    conn = get_redis_connection()
    worker = Worker(queues or ["default"], connection=conn)
    worker.work(with_scheduler=False)
