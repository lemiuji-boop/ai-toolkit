#!/usr/bin/env bash
# Пакетный экспорт и анализ КД: PDF/STEP → /api/jobs → data/exports/
# Использование:
#   ./scripts/export-and-analyze.sh
#   SOURCE_FOLDER=/media/data/work/MCC EXPORT_WORKERS=2 ./scripts/export-and-analyze.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_FOLDER="${SOURCE_FOLDER:-/media/data/work/MCC}"
EXPORTS_DIR="${EXPORTS_DIR:-$ROOT/data/exports}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8123}"
EXPORT_WORKERS="${EXPORT_WORKERS:-1}"
VLM_MODEL="${VLM_MODEL:-qwen3-vl:8b}"

health_ok() {
  curl -sf -m 3 "${BACKEND_URL}/health" >/dev/null 2>&1
}

start_backend() {
  echo "→ Запуск бэкенда ${BACKEND_URL}…"
  cd "$ROOT/backend"
  if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  export VLM_MODEL
  nohup uvicorn app.main:app --host 127.0.0.1 --port 8123 \
    >"$ROOT/.export-backend.log" 2>&1 &
  echo $! >"$ROOT/.export-backend.pid"
  for _ in $(seq 1 40); do
    if health_ok; then
      echo "✓ Бэкенд доступен"
      return 0
    fi
    sleep 0.5
  done
  echo "Ошибка: бэкенд не поднялся, см. $ROOT/.export-backend.log" >&2
  exit 1
}

check_ollama() {
  if curl -sf -m 3 "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
    echo "✓ Ollama :11434"
    if curl -sf "http://127.0.0.1:11434/api/tags" | grep -q "$VLM_MODEL"; then
      echo "✓ VLM: $VLM_MODEL"
    else
      echo "⚠ Модель $VLM_MODEL не найдена в Ollama — возможна заглушка vision"
    fi
  else
    echo "⚠ Ollama недоступен — vision будет stub" >&2
  fi
}

if health_ok; then
  echo "✓ Бэкенд уже запущен: ${BACKEND_URL}"
else
  start_backend
fi

check_ollama

mkdir -p "$EXPORTS_DIR"/{drawings,models,reports,jobs}

cd "$ROOT/backend"
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "→ Экспорт из: $SOURCE_FOLDER"
echo "→ Workers:    $EXPORT_WORKERS"

BACKEND_URL="$BACKEND_URL" \
  python3 "$ROOT/scripts/export_analyze.py" \
    --source "$SOURCE_FOLDER" \
    --exports "$EXPORTS_DIR" \
    --backend "$BACKEND_URL" \
    --workers "$EXPORT_WORKERS"

echo "✓ Готово: $EXPORTS_DIR/report_summary.json"
