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

set -euo pipefail
ARCHIVE="${1:?Укажите путь к backup .tar.gz}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP=$(mktemp -d)
tar -xzf "$ARCHIVE" -C "$TMP"
DIR=$(find "$TMP" -name "postgres.sql" -printf '%h\n' | head -1)

echo "Restore PostgreSQL..."
docker compose -f "$ROOT/infra/docker-compose.yml" exec -T postgres \
  psql -U ai_matnorm ai_matnorm < "$DIR/postgres.sql"
echo "Готово. MinIO восстановите вручную по README в архиве."
