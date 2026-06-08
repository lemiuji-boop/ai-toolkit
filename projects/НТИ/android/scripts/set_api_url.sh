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

# Задать URL API и пересобрать prod APK
set -euo pipefail
URL="${1:?Usage: $0 <http://IP:8010/ или https://tunnel-url/>}"
cd "$(dirname "$0")/.."
[[ "${URL}" == */ ]] || URL="${URL}/"
PROPS="local.properties"
if grep -q '^ntiApiBaseUrl=' "${PROPS}" 2>/dev/null; then
  sed -i "s|^ntiApiBaseUrl=.*|ntiApiBaseUrl=${URL}|" "${PROPS}"
else
  echo "ntiApiBaseUrl=${URL}" >> "${PROPS}"
fi
echo "ntiApiBaseUrl=${URL}"
./gradlew :app:assembleProdDebug -q
if adb get-state 2>/dev/null | grep -q device; then
  adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk
fi
