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
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT="$ROOT/backups/backup_$STAMP"
mkdir -p "$OUT"

echo "Backup PostgreSQL..."
docker compose -f "$ROOT/infra/docker-compose.yml" exec -T postgres \
  pg_dump -U ai_matnorm ai_matnorm > "$OUT/postgres.sql"

echo "Backup MinIO metadata note..."
echo "Скопируйте bucket ai-matnorm и ai-matnorm-quarantine через mc mirror" > "$OUT/minio_README.txt"

tar -czf "$OUT.tar.gz" -C "$ROOT/backups" "backup_$STAMP"
echo "Готово: $OUT.tar.gz"
