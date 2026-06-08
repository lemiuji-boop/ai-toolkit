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

# Установка prod APK: Wi‑Fi (IP ПК). USB reverse — только для отладки.
set -euo pipefail
cd "$(dirname "$0")/.."
"$(dirname "$0")/detect_api_url.sh"

if adb get-state 2>/dev/null | grep -q device; then
  IP=$(grep '^ntiApiBaseUrl=' local.properties | cut -d= -f2 | sed 's|http://||;s|/.*||')
  PORT="${NTI_PORT:-8010}"
  if adb shell "toybox nc -w 3 ${IP} ${PORT} </dev/null" 2>/dev/null; then
    echo "Wi‑Fi: телефон видит сервер ${IP}:${PORT}"
  else
    echo "ВНИМАНИЕ: с телефона порт ${PORT} недоступен. Выполните на ПК:"
    echo "  sudo ufw allow ${PORT}/tcp && sudo ufw reload"
    echo "Или для интернета: backend/scripts/tunnel_public.sh + HTTPS URL в local.properties"
  fi
fi

./gradlew :app:assembleProdDebug
adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk
echo "Установлено: ru.nti.sbor — API $(grep ntiApiBaseUrl local.properties)"
