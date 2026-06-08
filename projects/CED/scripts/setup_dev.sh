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

# Первичная настройка перед docker compose / pytest
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Создан .env из .env.example"
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  echo "Создано виртуальное окружение .venv"
fi

# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r backend/requirements.txt -r ai_agent/requirements.txt pytest

if [[ ! -d web_client/dist ]]; then
  (cd web_client && npm install && npm run build)
fi

echo "Готово. Запуск: docker compose up --build"
