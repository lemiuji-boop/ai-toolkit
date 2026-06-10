#!/usr/bin/env bash
# Гейт запрещённых паттернов (TZ-FINAL §3, T-00).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if rg -nE 'TODO|FIXME|NotImplementedError|source="stub"|_stub\(' \
  "$ROOT/backend/app" "$ROOT/addin" "$ROOT/admin" 2>/dev/null; then
  echo "ci-stub-gate: запрещённые паттерны найдены" >&2
  exit 1
fi
echo "ci-stub-gate: OK"
