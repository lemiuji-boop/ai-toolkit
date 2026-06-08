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

# Запуск API для локальной разработки (порт 8010)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
PORT="${NTI_PORT:-8010}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -e ".[dev]"

if ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
  echo "Порт ${PORT} занят — останавливаю старый uvicorn..."
  pkill -f "uvicorn app.main:app.*${PORT}" 2>/dev/null || true
  sleep 1
fi

echo "Сервер: http://0.0.0.0:${PORT}"
echo "Админка: http://127.0.0.1:${PORT}/admin/login  (admin / admin123)"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [[ -n "${IP}" ]]; then
  echo "Wi‑Fi:    http://${IP}:${PORT}/  (нужен: sudo ufw allow ${PORT}/tcp)"
  echo "Интернет: ./scripts/tunnel_and_build.sh"
fi

exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --reload
