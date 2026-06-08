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

# Записывает IP ПК в local.properties для сборки APK (телефон в той же Wi‑Fi)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
PORT="${NTI_PORT:-8010}"
if [[ -z "${IP}" ]]; then
  echo "Не удалось определить IP" >&2
  exit 1
fi
URL="http://${IP}:${PORT}/"
PROPS="${ROOT}/local.properties"
touch "${PROPS}"
if grep -q '^ntiApiBaseUrl=' "${PROPS}" 2>/dev/null; then
  sed -i "s|^ntiApiBaseUrl=.*|ntiApiBaseUrl=${URL}|" "${PROPS}"
else
  echo "ntiApiBaseUrl=${URL}" >> "${PROPS}"
fi
echo "ntiApiBaseUrl=${URL} → ${PROPS}"
