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

# Запуск всего стека НТИ.Сбор одной командой
set -euo pipefail
cd "$(dirname "$0")"

WITH_TUNNEL=false
DETACH="-d"
for arg in "$@"; do
  case "${arg}" in
    --tunnel|-t) WITH_TUNNEL=true ;;
    --foreground|-f) DETACH="" ;;
    -h|--help)
      echo "Использование: $0 [--tunnel] [--foreground]"
      echo "  --tunnel     также Cloudflare HTTPS (профиль internet)"
      echo "  --foreground без -d (логи в консоль)"
      exit 0
      ;;
  esac
done

echo "=== Сборка и запуск Docker ==="
if [[ "${WITH_TUNNEL}" == true ]]; then
  docker compose --profile internet up --build ${DETACH}
else
  docker compose up --build ${DETACH}
fi

if [[ -n "${DETACH}" ]]; then
  echo ""
  echo "Ожидание готовности API..."
  for _ in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${NTI_PORT:-8010}/api/v1/health" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

PORT="${NTI_PORT:-8010}"
IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)

echo ""
echo "=== НТИ.Сбор запущен ==="
echo "  API:     http://127.0.0.1:${PORT}/api/v1/health"
echo "  Админка: http://127.0.0.1:${PORT}/admin/login"
echo "           логин admin / пароль admin123"
echo "  Мобильный (Wi‑Fi): http://${IP:-<IP-ПК>}:${PORT}/"
echo "  Пользователи: ivanov/demo123, petrov/demo123 (+ из админки)"
echo ""
if [[ "${WITH_TUNNEL}" == true ]]; then
  echo "  HTTPS-туннель (для интернета):"
  sleep 3
  docker compose logs tunnel 2>/dev/null | grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' | tail -1 \
    || echo "    docker compose logs tunnel  # скопируйте URL в android/local.properties"
  echo "    затем: cd android && ./scripts/set_api_url.sh 'https://....../'"
fi
echo ""
echo "Остановка: docker compose down"
echo "С туннелем:  ./start.sh --tunnel"
