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

# Запуск API + подсказки по Wi‑Fi / туннелю
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${NTI_PORT:-8010}"

if ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
  echo "API уже слушает порт ${PORT}"
else
  echo "Запуск API на порту ${PORT}..."
  cd "${ROOT}"
  [[ -d .venv ]] || python3 -m venv .venv && .venv/bin/pip install -q -e ".[dev]"
  nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" > /tmp/nti_uvicorn.log 2>&1 &
  sleep 3
fi

if curl -sf "http://127.0.0.1:${PORT}/api/v1/health" >/dev/null; then
  echo "OK: http://127.0.0.1:${PORT}/api/v1/health"
else
  echo "ОШИБКА: API не отвечает. Лог: /tmp/nti_uvicorn.log" >&2
  tail -20 /tmp/nti_uvicorn.log >&2 || true
  exit 1
fi

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo "Админка:  http://127.0.0.1:${PORT}/admin/login  (admin / admin123)"
echo "Wi‑Fi:    http://${IP}:${PORT}/  →  sudo ufw allow ${PORT}/tcp"
echo "Туннель:  ./scripts/tunnel_and_build.sh  (интернет без USB)"
echo "Проверка: ./scripts/setup_wifi.sh"
