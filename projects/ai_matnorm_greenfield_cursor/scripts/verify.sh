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

# Полная локальная проверка (M0 + baseline)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Docker compose config =="
docker compose -f infra/docker-compose.yml config -q >/dev/null

echo "== Backend tests =="
cd "$ROOT/backend"
if [[ -x .venv/bin/pytest ]]; then
  .venv/bin/pytest -q
else
  python3 -m pytest -q
fi

echo "== Frontend build =="
cd "$ROOT/frontend"
npm run build

echo "== API smoke (optional) =="
if curl -sf http://127.0.0.1:8001/api/v1/health >/dev/null 2>&1; then
  HEALTH=$(curl -sf http://127.0.0.1:8001/api/v1/health)
  echo "$HEALTH"
  if echo "$HEALTH" | grep -q '"database":"ok"'; then
    curl -sf -X POST http://127.0.0.1:8001/api/v1/auth/login \
      -H 'Content-Type: application/json' \
      -d '{"email":"admin@example.com","password":"admin_change_me"}' | head -c 80
    echo " ... login OK"
  else
    echo "WARN: database not ok — run: docker compose -f infra/docker-compose.yml up -d postgres"
  fi
else
  echo "SKIP: API not running on :8001"
fi

echo "== verify.sh OK =="
