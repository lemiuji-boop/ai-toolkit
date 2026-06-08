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

# Публичный HTTPS-туннель к локальному API (интернет без проброса портов на роутере)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID="$(cd "${ROOT}/../android" && pwd)"
LOCAL_PORT="${NTI_PORT:-8010}"
PROPS="${ANDROID}/local.properties"

echo "Локальный API должен работать: http://127.0.0.1:${LOCAL_PORT}/api/v1/health"
echo ""

if command -v cloudflared >/dev/null 2>&1; then
  echo "Запуск Cloudflare Tunnel (HTTPS)..."
  echo "Скопируйте URL вида https://....trycloudflare.com в ${PROPS}:"
  echo "  ntiApiBaseUrl=https://ВАШ-URL/"
  echo ""
  echo "После появления URL — в другом терминале:"
  echo "  cd ${ANDROID} && ./gradlew assembleProdDebug && adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk"
  echo ""
  exec cloudflared tunnel --url "http://127.0.0.1:${LOCAL_PORT}"
fi

if command -v ngrok >/dev/null 2>&1; then
  echo "Запуск ngrok..."
  exec ngrok http "${LOCAL_PORT}"
fi

echo "Установите cloudflared или ngrok:" >&2
echo "  sudo apt install cloudflared   # или скачайте с developers.cloudflare.com" >&2
echo "  https://ngrok.com/download" >&2
exit 1
