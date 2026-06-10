#!/usr/bin/env bash
# Предполётная проверка стека МАТНОРМ перед тестовым развёртыванием.
# Использование: ./scripts/preflight.sh
# Выход: 0 — всё готово; 1 — есть провалы (см. ✗ в чек-листе).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8123}"
RAG_PORT="${RAG_PORT:-8020}"
ADMIN_PORT="${ADMIN_PORT:-3010}"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
FAIL=0

ok()   { printf '  ✓ %s\n' "$1"; }
bad()  { printf '  ✗ %s\n' "$1"; FAIL=1; }
warn() { printf '  ⚠ %s\n' "$1"; }

echo "=== МАТНОРМ preflight ==="

# --- Ollama и модели ---
echo "[1/7] Ollama"
TAGS="$(curl -sf -m 5 "$OLLAMA_URL/api/tags" 2>/dev/null || true)"
if [[ -n "$TAGS" ]]; then
  COUNT="$(echo "$TAGS" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["models"]))' 2>/dev/null || echo '?')"
  ok "Ollama доступен (${OLLAMA_URL}), моделей: ${COUNT}"
  VLM="$(grep -E '^VLM_MODEL=' "$ROOT/backend/.env" 2>/dev/null | cut -d= -f2 || true)"
  if [[ -n "$VLM" ]]; then
    if echo "$TAGS" | grep -q "\"name\":\"${VLM}"; then
      ok "VLM-модель установлена: ${VLM}"
    else
      bad "VLM-модель '${VLM}' не найдена в Ollama (ollama pull ${VLM})"
    fi
  fi
  if echo "$TAGS" | grep -q '"name":"nomic-embed-text'; then
    ok "Embed-модель установлена: nomic-embed-text"
  else
    warn "nomic-embed-text не найдена (RAG перейдёт на fallback-backend)"
  fi
else
  bad "Ollama недоступен по ${OLLAMA_URL}"
fi

# --- Порты ---
echo "[2/7] Порты"
for entry in "backend:${BACKEND_PORT}" "rag:${RAG_PORT}" "admin:${ADMIN_PORT}"; do
  name="${entry%%:*}"; port="${entry##*:}"
  if ss -tln 2>/dev/null | grep -q ":${port} "; then
    ok "Порт ${port} (${name}) слушается"
  else
    warn "Порт ${port} (${name}) свободен — сервис не запущен (scripts/start-matnorm-stack.sh)"
  fi
done

# --- TLS-сертификат ---
echo "[3/7] TLS-сертификат LAN"
if [[ -f "$ROOT/deploy/certs/lan.crt" && -f "$ROOT/deploy/certs/lan.key" ]]; then
  EXP="$(openssl x509 -enddate -noout -in "$ROOT/deploy/certs/lan.crt" 2>/dev/null | cut -d= -f2 || true)"
  ok "Сертификат есть (deploy/certs/lan.crt, истекает: ${EXP:-?})"
  if openssl x509 -checkend 604800 -noout -in "$ROOT/deploy/certs/lan.crt" >/dev/null 2>&1; then
    ok "Сертификат действителен ещё минимум 7 дней"
  else
    bad "Сертификат истекает в течение 7 дней — перегенерируйте scripts/gen-lan-cert.sh"
  fi
else
  bad "Нет deploy/certs/lan.{crt,key} — выполните scripts/gen-lan-cert.sh <LAN_IP>"
fi

# --- rules.json ---
echo "[4/7] Нормативные правила"
RULES="$ROOT/backend/app/data/rules.json"
if [[ -f "$RULES" ]]; then
  VER="$(python3 -c "import json; print(json.load(open('$RULES')).get('version','?'))" 2>/dev/null || echo '?')"
  ok "rules.json найден, version=${VER}"
else
  bad "Нет backend/app/data/rules.json"
fi

# --- .env и SECRET_KEY ---
echo "[5/7] Конфигурация"
if [[ -f "$ROOT/backend/.env" ]]; then
  ok "backend/.env найден"
  if grep -qE '^SECRET_KEY=.{16,}' "$ROOT/backend/.env" \
     && ! grep -q '^SECRET_KEY=change-me' "$ROOT/backend/.env"; then
    ok "SECRET_KEY задан"
  else
    bad "SECRET_KEY не задан или дефолтный (openssl rand -hex 32 → backend/.env)"
  fi
  if grep -qE '^ALLOW_EXTERNAL_PROVIDERS=1' "$ROOT/backend/.env"; then
    warn "ALLOW_EXTERNAL_PROVIDERS=1 — разрешены исходящие вызовы (SEC-001!)"
  else
    ok "Внешние провайдеры выключены (SEC-001 соблюдается)"
  fi
else
  bad "Нет backend/.env (скопируйте backend/.env.example)"
fi
if [[ -f "$ROOT/addin/lan-host.txt" ]]; then
  ok "LAN IP сервера: $(tr -d '[:space:]' <"$ROOT/addin/lan-host.txt")"
else
  warn "Нет addin/lan-host.txt — определится при start-matnorm-stack.sh"
fi

# --- Каталоги данных ---
echo "[6/7] Каталоги данных"
for d in data/incoming data/incoming/drawings data/incoming/models data/admin data/exports data/rag; do
  if [[ -d "$ROOT/$d" ]]; then
    ok "$d/"
  else
    mkdir -p "$ROOT/$d" && ok "$d/ (создан)"
  fi
done

# --- Диск ---
echo "[7/7] Диск"
AVAIL_GB="$(df -BG --output=avail "$ROOT" | tail -1 | tr -dc '0-9')"
if [[ "${AVAIL_GB:-0}" -ge 10 ]]; then
  ok "Свободно ${AVAIL_GB} ГБ (>= 10 ГБ)"
else
  bad "Мало места: ${AVAIL_GB:-?} ГБ (нужно >= 10 ГБ для моделей/индексов)"
fi

echo ""
if [[ "$FAIL" -eq 0 ]]; then
  echo "=== Готово: все обязательные проверки пройдены ==="
else
  echo "=== Есть провалы (✗) — устраните перед развёртыванием ==="
fi
exit "$FAIL"
