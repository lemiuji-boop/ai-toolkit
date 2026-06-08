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

# Подготовка доступа по Wi‑Fi: IP, файрвол, проверка с телефона
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID="$(cd "${ROOT}/../android" && pwd)"
PORT="${NTI_PORT:-8010}"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')

if [[ -z "${IP}" ]]; then
  echo "Не удалось определить IP ПК" >&2
  exit 1
fi

echo "=== НТИ.Сбор: Wi‑Fi ==="
echo "IP ПК: ${IP}"
echo "URL API: http://${IP}:${PORT}/"
echo ""

if command -v ufw >/dev/null 2>&1; then
  echo "Откройте порт на ПК (один раз, нужен пароль sudo):"
  echo "  sudo ufw allow ${PORT}/tcp"
  echo "  sudo ufw reload"
  echo ""
fi

if adb get-state 2>/dev/null | grep -q device; then
  echo "Проверка с телефона (adb)..."
  if adb shell "toybox nc -w 3 ${IP} ${PORT} </dev/null" 2>/dev/null; then
    echo "OK: телефон видит порт ${PORT}"
  else
    echo "FAIL: порт ${PORT} с телефона недоступен — выполните sudo ufw allow ${PORT}/tcp"
    echo "      или отключите файрвол для частной сети."
  fi
  echo ""
fi

"${ANDROID}/scripts/detect_api_url.sh"
echo "Далее: cd ${ANDROID} && ./gradlew assembleProdDebug && adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk"
