#!/usr/bin/env bash
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

# Smoke-тест MVP: создать выпуск, сгенерировать (sync fallback), утвердить
set -e
API="${API_URL:-http://localhost:8000}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "API: $API"

EP=$(curl -sf -X POST "$API/episodes" \
  -H "Content-Type: application/json" \
  -d '{"topic":"жерло вулкана","duration_target":60,"platforms":["instagram","tiktok","youtube_shorts"],"language":"ru"}')
EP_ID=$(echo "$EP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created episode: $EP_ID"

# Синхронный пайплайн (если Celery не запущен)
cd "$ROOT/services/api"
source .venv/bin/activate
python3 -c "
import asyncio
from uuid import UUID
from app.orchestrator.pipeline import EpisodePipeline
from app.db.session import async_session_factory

async def main():
    async with async_session_factory() as s:
        await EpisodePipeline().run(s, UUID('$EP_ID'))
asyncio.run(main())
"
echo "Pipeline done"

curl -sf -X POST "$API/episodes/$EP_ID/approve" > /dev/null
DETAIL=$(curl -sf "$API/episodes/$EP_ID")
STATUS=$(echo "$DETAIL" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
echo "Final status: $STATUS"
[ "$STATUS" = "approved" ] && echo "SMOKE OK" || (echo "SMOKE FAILED"; exit 1)
