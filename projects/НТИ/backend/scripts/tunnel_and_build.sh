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

# Туннель HTTPS + сборка APK (работа через мобильный интернет)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID="$(cd "${ROOT}/../android" && pwd)"
PORT="${NTI_PORT:-8010}"
LOG="/tmp/nti_cloudflared.log"

pkill -f "cloudflared tunnel --url http://127.0.0.1:${PORT}" 2>/dev/null || true
nohup cloudflared tunnel --url "http://127.0.0.1:${PORT}" > "${LOG}" 2>&1 &
echo "Ожидание URL туннеля..."
for _ in $(seq 1 30); do
  URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "${LOG}" | head -1)
  if [[ -n "${URL}" ]]; then
    echo "Туннель: ${URL}"
    "${ANDROID}/scripts/set_api_url.sh" "${URL}/"
    exit 0
  fi
  sleep 1
done
echo "URL не получен. Лог: ${LOG}" >&2
exit 1
