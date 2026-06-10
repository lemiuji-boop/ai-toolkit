#!/usr/bin/env bash
# Полный стек МАТНОРМ: бэкенд (HTTPS LAN) + статика add-in + RAG + админ.
# По умолчанию — только локальная сеть (без Cloudflare tunnel).
#
# Использование:
#   ./scripts/start-matnorm-stack.sh                  # LAN HTTPS (по умолчанию)
#   FORCE_RESTART=1 ./scripts/start-matnorm-stack.sh  # перезапуск даже если живы (новый код)
#   USE_TUNNEL=1 ./scripts/start-matnorm-stack.sh     # + Cloudflare quick tunnel (отладка)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8123}"
RAG_PORT="${RAG_PORT:-8020}"
ADMIN_PORT="${ADMIN_PORT:-3010}"
LISTEN_HOST="${LISTEN_HOST:-0.0.0.0}"
USE_TUNNEL="${USE_TUNNEL:-0}"
FORCE_RESTART="${FORCE_RESTART:-0}"
VLM_MODEL="${VLM_MODEL:-qwen3-vl:8b}"
CERT_KEY="$ROOT/deploy/certs/lan.key"
CERT_CRT="$ROOT/deploy/certs/lan.crt"
LAN_HOST_FILE="$ROOT/addin/lan-host.txt"

detect_lan_ip() {
  if [[ -f "$LAN_HOST_FILE" ]]; then
    local saved
    saved="$(tr -d '[:space:]' <"$LAN_HOST_FILE")"
    if [[ -n "$saved" ]]; then
      echo "$saved"
      return 0
    fi
  fi
  hostname -I | awk '{print $1}'
}

save_lan_ip() {
  local ip="$1"
  echo "$ip" >"$LAN_HOST_FILE"
}

LAN_IP="$(detect_lan_ip)"
if [[ -z "$LAN_IP" ]]; then
  echo "Ошибка: не удалось определить LAN IP" >&2
  exit 1
fi
save_lan_ip "$LAN_IP"

BACKEND_URL="https://${LAN_IP}:${BACKEND_PORT}"
export BACKEND_URL

health_ok() {
  curl -skf -m 3 "${BACKEND_URL}/health" >/dev/null 2>&1
}

health_ok_local() {
  curl -skf -m 3 "https://127.0.0.1:${BACKEND_PORT}/health" >/dev/null 2>&1 \
    || curl -sf -m 2 "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null 2>&1
}

rag_health_ok() {
  curl -sf -m 2 "http://127.0.0.1:${RAG_PORT}/health" >/dev/null 2>&1
}

stop_old_backend() {
  if [[ -f "$ROOT/.matnorm-backend.pid" ]]; then
    local pid
    pid="$(cat "$ROOT/.matnorm-backend.pid" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 0.5
    fi
    rm -f "$ROOT/.matnorm-backend.pid"
  fi
  # HTTP-инстанс без TLS (предыдущий режим)
  while read -r pid _; do
    [[ -n "$pid" ]] || continue
    if ps -p "$pid" -o args= 2>/dev/null | grep -q "app.main:app.*--port ${BACKEND_PORT}"; then
      kill "$pid" 2>/dev/null || true
    fi
  done < <(pgrep -f "uvicorn app.main:app.*--port ${BACKEND_PORT}" 2>/dev/null || true)
}

start_rag() {
  if ss -tln 2>/dev/null | grep -q "127.0.0.1:${RAG_PORT} "; then
    if [[ -f "$ROOT/.matnorm-rag.pid" ]]; then
      pid="$(cat "$ROOT/.matnorm-rag.pid" 2>/dev/null || true)"
      [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
    fi
    sleep 0.3
  fi
  LISTEN_HOST="$LISTEN_HOST" RAG_PORT="$RAG_PORT" "$ROOT/scripts/start-rag.sh"
}

start_admin() {
  # Перезапуск, если старый инстанс слушал только 127.0.0.1
  if ss -tln 2>/dev/null | grep -q "127.0.0.1:${ADMIN_PORT} "; then
    if [[ -f "$ROOT/.admin-static.pid" ]]; then
      pid="$(cat "$ROOT/.admin-static.pid" 2>/dev/null || true)"
      [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
    fi
    sleep 0.3
  fi
  LISTEN_HOST="$LISTEN_HOST" ADMIN_PORT="$ADMIN_PORT" BACKEND_URL="$BACKEND_URL" \
    "$ROOT/scripts/start-admin.sh"
}

start_backend() {
  echo "→ Бэкенд ${BACKEND_URL} (add-in static /addin/, TLS)"
  "$ROOT/scripts/gen-lan-cert.sh" "$LAN_IP"

  cd "$ROOT/backend"
  if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  export VLM_MODEL
  # CORS: LAN HTTPS origin + опционально подсеть 192.168.*
  export CORS_ORIGINS="[\"${BACKEND_URL}\",\"https://127.0.0.1:${BACKEND_PORT}\",\"http://127.0.0.1:${BACKEND_PORT}\",\"http://127.0.0.1:${ADMIN_PORT}\",\"http://localhost:${ADMIN_PORT}\"]"
  export CORS_ORIGIN_REGEX="${CORS_ORIGIN_REGEX:-^https://192\\.168\\.[0-9]+\\.[0-9]+(:[0-9]+)?$}"

  stop_old_backend

  nohup uvicorn app.main:app \
    --host "$LISTEN_HOST" \
    --port "$BACKEND_PORT" \
    --ssl-keyfile "$CERT_KEY" \
    --ssl-certfile "$CERT_CRT" \
    >"$ROOT/.matnorm-backend.log" 2>&1 &
  echo $! >"$ROOT/.matnorm-backend.pid"

  for _ in $(seq 1 40); do
    if health_ok; then
      echo "✓ Backend: ${BACKEND_URL}"
      return 0
    fi
    sleep 0.5
  done
  echo "Ошибка бэкенда, см. $ROOT/.matnorm-backend.log" >&2
  exit 1
}

package_addin() {
  LAN_BASE_URL="$BACKEND_URL" "$ROOT/scripts/package-addin.sh"
}

echo "=== МАТНОРМ LAN mode ==="
echo "  Server IP: ${LAN_IP}"
echo "  USE_TUNNEL=${USE_TUNNEL}"

# On-premise: tunnel выключен по умолчанию
"$ROOT/scripts/stop-tunnel.sh"

if [[ "$FORCE_RESTART" == "1" ]]; then
  echo "→ FORCE_RESTART=1 — перезапуск бэкенда с новым кодом…"
  stop_old_backend
  start_backend
elif health_ok; then
  echo "✓ Бэкенд уже запущен (HTTPS)"
elif health_ok_local; then
  echo "⚠ Бэкенд на :${BACKEND_PORT} без LAN TLS — перезапуск…"
  stop_old_backend
  start_backend
else
  start_backend
fi

start_rag
package_addin
start_admin

echo ""
echo "=== МАТНОРМ stack (LAN) ==="
echo "  API:     ${BACKEND_URL}"
echo "  Health:  ${BACKEND_URL}/health"
echo "  RAG:     http://${LAN_IP}:${RAG_PORT}"
echo "  Admin:   http://${LAN_IP}:${ADMIN_PORT}/"
echo "  Add-in:  ${BACKEND_URL}/addin/taskpane.html"
echo "  Sideload: addin/dist/manifest.xml или addin/matnorm-addin.zip"
echo ""
echo "Firewall (если ufw активен): sudo ufw allow ${BACKEND_PORT}/tcp"
echo "Проверка: curl -k ${BACKEND_URL}/health"

if [[ "$USE_TUNNEL" == "1" ]]; then
  echo ""
  echo "→ Запуск Cloudflare tunnel (опционально, USE_TUNNEL=1)…"
  TUNNEL_TARGET="http://127.0.0.1:${BACKEND_PORT}" "$ROOT/scripts/start-tunnel.sh"
  if [[ -f "$ROOT/.tunnel-url" ]]; then
    echo "  Tunnel: $(cat "$ROOT/.tunnel-url")"
  fi
fi
