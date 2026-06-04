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

# Запуск инфраструктуры и подсказки для dev-сервисов
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

docker compose -f infra/docker-compose.yml up -d

echo ""
echo "Infrastructure is up. Run in separate terminals:"
echo ""
echo "  # API"
echo "  cd services/api && source .venv/bin/activate && alembic upgrade head && uvicorn app.main:app --reload --port 8000"
echo ""
echo "  # Celery"
echo "  cd services/api && source .venv/bin/activate && celery -A app.celery_app worker --loglevel=info"
echo ""
echo "  # Web"
echo "  npm run dev:web"
echo ""
