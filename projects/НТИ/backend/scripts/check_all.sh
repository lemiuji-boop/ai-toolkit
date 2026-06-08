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

# Полная проверка: API, админка, Wi‑Fi с телефона, туннель
set -u
PORT="${NTI_PORT:-8010}"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
OK=0
FAIL=0

pass() { echo "  OK: $1"; OK=$((OK + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== НТИ.Сбор: проверка ==="
echo ""

echo "[1] API localhost:${PORT}"
if curl -sf -m 3 "http://127.0.0.1:${PORT}/api/v1/health" >/dev/null; then
  pass "health"
else
  fail "health — запустите ./scripts/start_all.sh"
fi
if curl -sf -m 3 -o /dev/null "http://127.0.0.1:${PORT}/admin/login"; then
  pass "admin login page"
else
  fail "admin"
fi

echo "[2] Вход ivanov/demo123"
LOGIN=$(curl -sf -m 5 -X POST "http://127.0.0.1:${PORT}/api/v1/mobile/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"ivanov","password":"demo123"}' 2>/dev/null || true)
if echo "${LOGIN}" | grep -q access_token; then
  pass "login"
else
  fail "login (${LOGIN})"
fi

echo "[3] Wi‑Fi с телефона (${IP})"
if adb get-state 2>/dev/null | grep -q device; then
  if adb shell "toybox nc -w 3 ${IP} ${PORT} </dev/null" 2>/dev/null; then
    pass "порт ${PORT} с телефона"
  else
    fail "порт ${PORT} — выполните: sudo ufw allow ${PORT}/tcp"
  fi
else
  echo "  SKIP: телефон не подключён"
fi

echo "[4] Туннель HTTPS"
URL=""
for f in /tmp/nti_cf.log /tmp/nti_cloudflared.log; do
  [[ -f "${f}" ]] && URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "${f}" 2>/dev/null | head -1)
  [[ -n "${URL}" ]] && break
done
if [[ -n "${URL}" ]] && curl -sf -m 15 "${URL}/api/v1/health" >/dev/null; then
  pass "туннель ${URL}"
else
  echo "  SKIP: ./scripts/tunnel_and_build.sh"
fi

echo ""
echo "Итого: OK=${OK} FAIL=${FAIL}"
exit $((FAIL > 0 ? 1 : 0))
