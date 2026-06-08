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

# Проброс Ollama (127.0.0.1:11434) на docker0 для контейнеров CED (11435).
set -euo pipefail
BIND="${OLLAMA_BRIDGE_BIND:-172.17.0.1}"
PORT="${OLLAMA_BRIDGE_PORT:-11435}"
TARGET="${OLLAMA_TARGET:-127.0.0.1:11434}"

if ! command -v socat >/dev/null; then
  echo "Установите socat: sudo apt install socat"
  exit 1
fi

if ss -tln | grep -q ":${PORT} "; then
  echo "Порт ${PORT} уже слушает — мост, вероятно, запущен."
  exit 0
fi

echo "Мост ${BIND}:${PORT} -> ${TARGET}"
exec socat "TCP-LISTEN:${PORT},bind=${BIND},reuseaddr,fork" "TCP:${TARGET}"
