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

# Разрешить входящие на порт API с телефона в Wi‑Fi (требуется sudo)
set -euo pipefail
PORT="${NTI_PORT:-8010}"
echo "Открываю TCP ${PORT}..."
if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow "${PORT}/tcp"
  sudo ufw reload
  sudo ufw status | grep "${PORT}" || true
else
  sudo iptables -I INPUT -p tcp --dport "${PORT}" -j ACCEPT
  echo "Правило iptables добавлено для порта ${PORT}"
fi
echo "Проверка: ./scripts/setup_wifi.sh"
