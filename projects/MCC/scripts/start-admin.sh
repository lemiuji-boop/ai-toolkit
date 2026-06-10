#!/usr/bin/env bash
# Запуск админ-панели МАТНОРМ и проверка бэкенда.
# Порт 3010 (3001 часто занят AnythingLLM на хосте).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8123}"
ADMIN_PORT="${ADMIN_PORT:-3010}"
LISTEN_HOST="${LISTEN_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8123}"
PID_FILE="$ROOT/.admin-static.pid"
LOG_FILE="$ROOT/.admin-static.log"

health_ok() {
  if [[ "$BACKEND_URL" == https://* ]]; then
    curl -skf -m 3 "${BACKEND_URL}/health" >/dev/null 2>&1
  else
    curl -sf -m 2 "${BACKEND_URL}/health" >/dev/null 2>&1
  fi
}

admin_ok() {
  curl -sf -m 2 "http://${LISTEN_HOST}:${ADMIN_PORT}/" >/dev/null 2>&1 \
    || curl -sf -m 2 "http://127.0.0.1:${ADMIN_PORT}/" >/dev/null 2>&1
}

start_backend() {
  if [[ "$BACKEND_URL" == https://* ]]; then
    echo "→ Бэкенд HTTPS: запустите ./scripts/start-matnorm-stack.sh" >&2
    exit 1
  fi
  echo "→ Запуск бэкенда на порту ${BACKEND_PORT}…"
  cd "$ROOT/backend"
  if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  nohup uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" \
    >"$ROOT/.admin-backend.log" 2>&1 &
  echo $! >"$ROOT/.admin-backend.pid"
  for _ in $(seq 1 30); do
    if health_ok; then
      echo "✓ Бэкенд доступен: ${BACKEND_URL}"
      return 0
    fi
    sleep 0.5
  done
  echo "Ошибка: бэкенд не поднялся, см. $ROOT/.admin-backend.log" >&2
  exit 1
}

start_admin_static() {
  cd "$ROOT/admin"
  nohup python3 -m http.server "$ADMIN_PORT" --bind "$LISTEN_HOST" \
    >"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
  for _ in $(seq 1 20); do
    if admin_ok; then
      echo "✓ Админ-панель: http://${LISTEN_HOST}:${ADMIN_PORT}/"
      return 0
    fi
    sleep 0.25
  done
  echo "Ошибка: админ-панель не отвечает, см. $LOG_FILE" >&2
  exit 1
}

if health_ok; then
  echo "✓ Бэкенд уже запущен: ${BACKEND_URL}"
else
  start_backend
fi

if admin_ok; then
  echo "✓ Админ-панель уже доступна: http://${LISTEN_HOST}:${ADMIN_PORT}/"
  echo "  API: ${BACKEND_URL}/api/admin/"
  exit 0
fi

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "⚠ Порт ${ADMIN_PORT} занят другим процессом (pid ${old_pid})" >&2
    exit 1
  fi
fi

echo "→ Админ-панель: http://${LISTEN_HOST}:${ADMIN_PORT}/"
echo "  API: ${BACKEND_URL}/api/admin/"
start_admin_static
