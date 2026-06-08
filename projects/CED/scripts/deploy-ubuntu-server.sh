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

# Развёртывание CED на едином Ubuntu-сервере (Docker + Ollama на хосте).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${CED_ENV_FILE:-$ROOT/.env}"
COMPOSE_FILES=(-f docker-compose.yml -f docker-compose.server.yml)

usage() {
  cat <<'EOF'
Использование: ./scripts/deploy-ubuntu-server.sh [--skip-web] [--down]

  --skip-web   не пересобирать web_client/dist
  --down       остановить стек

Требуется .env с CED_CATALOG_MOUNT (см. .env.server.example).
EOF
}

SKIP_WEB=0
ACTION=up

for arg in "$@"; do
  case "$arg" in
    --skip-web) SKIP_WEB=1 ;;
    --down) ACTION=down ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Неизвестный аргумент: $arg"; usage; exit 1 ;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[CED] Нет $ENV_FILE — скопируйте: cp .env.server.example .env"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ "$ACTION" == "down" ]]; then
  docker compose "${COMPOSE_FILES[@]}" down
  exit 0
fi

if [[ -z "${CED_CATALOG_MOUNT:-}" ]]; then
  echo "[CED] Задайте CED_CATALOG_MOUNT в .env (путь к смонтированному каталогу КД)"
  exit 1
fi

if [[ ! -d "$CED_CATALOG_MOUNT" ]]; then
  echo "[CED] Каталог не найден: $CED_CATALOG_MOUNT"
  echo "      Смонтируйте share после OpenVPN — см. docs/deployment/ubuntu-single-server.md"
  exit 1
fi

if ! command -v socat >/dev/null; then
  echo "[CED] Установите socat: sudo apt install -y socat"
  exit 1
fi

if ! pgrep -f 'socat.*11435' >/dev/null 2>&1; then
  echo "[CED] Мост Ollama 172.17.0.1:11435 → 127.0.0.1:11434 ..."
  nohup "$ROOT/scripts/ollama-docker-bridge.sh" >> /tmp/ced-ollama-bridge.log 2>&1 &
  sleep 1
fi

if [[ "$SKIP_WEB" -eq 0 ]] && [[ -f "$ROOT/web_client/package.json" ]]; then
  echo "[CED] Сборка веб-клиента (API через nginx /api) ..."
  (cd "$ROOT/web_client" && npm ci --silent 2>/dev/null || npm install --silent)
  (cd "$ROOT/web_client" && npm run build)
fi

if [[ ! -f "$ROOT/web_client/dist/index.html" ]]; then
  echo "[CED] Нет web_client/dist — выполните npm run build в web_client"
  exit 1
fi

echo "[CED] Docker compose up ..."
docker compose "${COMPOSE_FILES[@]}" up -d --build

HOST="${CED_PUBLIC_HOST:-$(hostname -I | awk '{print $1}')}"
echo ""
echo "[CED] Готово:"
echo "  Браузер (модераторы):  http://${HOST}/"
echo "  WinForms / API:        http://${HOST}:8000"
echo "  Health:                curl -s http://${HOST}/api/health"
echo "  Ollama (хост):         curl -s http://127.0.0.1:11434/api/tags"
echo "  Логин по умолчанию:    admin / admin  (сменить после входа)"
