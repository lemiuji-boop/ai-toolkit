#!/usr/bin/env bash
# Временный Cloudflare Tunnel к локальным сервисам МАТНОРМ.
# Quick tunnel (без аккаунта) или named tunnel через CLOUDFLARE_TUNNEL_TOKEN.
#
# Использование:
#   ./scripts/start-tunnel.sh              # quick → backend :8123
#   TUNNEL_TARGET=http://127.0.0.1:8123 ./scripts/start-tunnel.sh
#   CLOUDFLARE_TUNNEL_TOKEN=... ./scripts/start-tunnel.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TUNNEL_TARGET="${TUNNEL_TARGET:-http://127.0.0.1:8123}"
ADDIN_DIR="$ROOT/addin"
URL_FILE="$ROOT/.tunnel-url"
LOG_FILE="$ROOT/.cloudflared.log"
PID_FILE="$ROOT/.cloudflared.pid"

find_cloudflared() {
  if command -v cloudflared >/dev/null 2>&1; then
    command -v cloudflared
    return 0
  fi
  if [[ -x "$ROOT/scripts/cloudflared" ]]; then
    echo "$ROOT/scripts/cloudflared"
    return 0
  fi
  echo ""
}

download_cloudflared() {
  local dest="$ROOT/scripts/cloudflared"
  echo "→ cloudflared не найден, загрузка в scripts/…"
  local url="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
  curl -fsSL "$url" -o "$dest"
  chmod +x "$dest"
  echo "$dest"
}

update_addin_config() {
  local url="$1"
  local cfg="$ADDIN_DIR/config.json"
  python3 - "$url" "$cfg" <<'PY'
import json, sys
url, path = sys.argv[1], sys.argv[2]
base = url.rstrip("/")
data = {
        "backendUrl": base,
        "addinUrl": f"{base}/addin",
        "tunnelUrl": base,
        "updatedAt": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"→ config.json: backendUrl={base}")
PY
  # Подстановка URL в dist/manifest (если есть)
  if [[ -f "$ADDIN_DIR/dist/manifest.xml" ]]; then
    sed -i "s|https://[^\"]*trycloudflare.com[^\"]*|${url}|g" "$ADDIN_DIR/dist/manifest.xml" 2>/dev/null || true
    sed -i "s|https://your-addin.vercel.app|${url}/addin|g" "$ADDIN_DIR/dist/manifest.xml" 2>/dev/null || true
  fi
}

wait_for_url() {
  local attempts="${1:-60}"
  for _ in $(seq 1 "$attempts"); do
    if [[ -f "$LOG_FILE" ]]; then
      local url
      url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG_FILE" | head -1 || true)
      if [[ -n "$url" ]]; then
        echo "$url"
        return 0
      fi
    fi
    sleep 0.5
  done
  return 1
}

CF="$(find_cloudflared)"
if [[ -z "$CF" ]]; then
  CF="$(download_cloudflared)"
fi

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "⚠ cloudflared уже запущен (pid $(cat "$PID_FILE"))"
  if [[ -f "$URL_FILE" ]]; then
    echo "  URL: $(cat "$URL_FILE")"
  fi
  exit 0
fi

: >"$LOG_FILE"

if [[ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]]; then
  echo "→ Named tunnel (token из CLOUDFLARE_TUNNEL_TOKEN)"
  nohup "$CF" tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN" >>"$LOG_FILE" 2>&1 &
else
  echo "→ Quick tunnel → $TUNNEL_TARGET"
  nohup "$CF" tunnel --url "$TUNNEL_TARGET" >>"$LOG_FILE" 2>&1 &
fi

echo $! >"$PID_FILE"
echo "→ cloudflared pid $(cat "$PID_FILE"), лог: $LOG_FILE"

if [[ -z "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]]; then
  TUNNEL_URL="$(wait_for_url 90)" || {
    echo "Ошибка: URL туннеля не получен, см. $LOG_FILE" >&2
    tail -20 "$LOG_FILE" >&2 || true
    exit 1
  }
  echo "$TUNNEL_URL" >"$URL_FILE"
  echo "✓ Tunnel URL: $TUNNEL_URL"
  update_addin_config "$TUNNEL_URL"
  echo ""
  echo "Add-in taskpane: ${TUNNEL_URL}/addin/taskpane.html"
  echo "Backend API:     ${TUNNEL_URL}/health"
else
  echo "Named tunnel: URL задаётся в Cloudflare Dashboard"
fi
