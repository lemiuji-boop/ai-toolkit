#!/usr/bin/env bash
# Запуск RAG-сервиса нормативов (СЕРВИС-05) на :8020.
# Использование:
#   ./scripts/start-rag.sh
#   EMBED_BACKEND=stub ./scripts/start-rag.sh   # без Ollama
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAG_PORT="${RAG_PORT:-8020}"
LISTEN_HOST="${LISTEN_HOST:-127.0.0.1}"
RAG_DIR="$ROOT/services/rag"

cd "$RAG_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -e ".[dev]"

mkdir -p "$ROOT/data/rag/chroma"

export PROJECT_ROOT="$ROOT"
export CHROMA_PATH="${CHROMA_PATH:-$ROOT/data/rag/chroma}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
export EMBED_BACKEND="${EMBED_BACKEND:-auto}"
export EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"
export AUTO_INGEST_CORPUS="${AUTO_INGEST_CORPUS:-true}"

health_ok() {
  curl -sf -m 2 "http://127.0.0.1:${RAG_PORT}/health" >/dev/null 2>&1
}

if health_ok; then
  echo "✓ RAG уже запущен на :${RAG_PORT}"
  exit 0
fi

echo "→ RAG :${RAG_PORT} (Chroma: ${CHROMA_PATH}, embed: ${EMBED_BACKEND})"
nohup uvicorn app.main:app --host "$LISTEN_HOST" --port "$RAG_PORT" \
  >"$ROOT/.matnorm-rag.log" 2>&1 &
echo $! >"$ROOT/.matnorm-rag.pid"

for _ in $(seq 1 40); do
  if health_ok; then
    echo "✓ RAG: http://127.0.0.1:${RAG_PORT}"
    curl -sf "http://127.0.0.1:${RAG_PORT}/version" | python3 -m json.tool 2>/dev/null || true
    exit 0
  fi
  sleep 0.5
done

echo "Ошибка RAG, см. $ROOT/.matnorm-rag.log" >&2
exit 1
