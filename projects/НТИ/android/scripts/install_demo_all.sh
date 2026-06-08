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

# Сборка и установка 4 демо-версий (НТИ.Сбор 1–4) на подключённый смартфон
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Сборка v1–v4 (debug) ==="
./gradlew assembleV1Debug assembleV2Debug assembleV3Debug assembleV4Debug

APK_DIR="app/build/outputs/apk"
install_apk() {
  local flavor=$1
  local apk="${APK_DIR}/${flavor}/debug/app-${flavor}-debug.apk"
  if [[ ! -f "$apk" ]]; then
    echo "APK не найден: $apk" >&2
    exit 1
  fi
  echo "=== Установка ${flavor} ==="
  adb install -r "$apk"
}

echo "=== Устройства ==="
adb devices

install_apk v1
install_apk v2
install_apk v3
install_apk v4

echo "Готово: на устройстве 4 иконки «НТИ.Сбор 1» … «НТИ.Сбор 4»"
