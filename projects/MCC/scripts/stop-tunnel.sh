#!/usr/bin/env bash
# Остановка Cloudflare quick tunnel (on-premise LAN не требует egress).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT/.cloudflared.pid"

stopped=0
if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    stopped=1
    echo "✓ cloudflared остановлен (pid $pid)"
  fi
  rm -f "$PID_FILE"
fi

while read -r pid _; do
  [[ -n "$pid" ]] || continue
  kill "$pid" 2>/dev/null || true
  stopped=1
  echo "✓ cloudflared остановлен (pid $pid)"
done < <(pgrep -f 'cloudflared tunnel' 2>/dev/null || true)

if [[ "$stopped" -eq 0 ]]; then
  echo "✓ cloudflared не запущен"
fi
