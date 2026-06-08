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

# Dev на Ubuntu: Docker CED + мост Ollama (локальный каталог ./data/catalog).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p "$ROOT/data/catalog"
export CED_CATALOG_MOUNT="${CED_CATALOG_MOUNT:-$ROOT/data/catalog}"

if ! pgrep -f 'socat.*11435' >/dev/null 2>&1; then
  echo "[CED] Мост Ollama 172.17.0.1:11435 ..."
  nohup "$ROOT/scripts/ollama-docker-bridge.sh" >> /tmp/ced-ollama-bridge.log 2>&1 &
  sleep 1
fi

echo "[CED] Docker compose (server profile) ..."
docker compose -f docker-compose.yml -f docker-compose.server.yml up -d --build

echo "[CED] Готово:"
echo "  Веб:    http://$(hostname -I | awk '{print $1}')/"
echo "  API:    http://127.0.0.1/api/health"
echo "  Ollama: curl http://127.0.0.1:11434/api/tags"
