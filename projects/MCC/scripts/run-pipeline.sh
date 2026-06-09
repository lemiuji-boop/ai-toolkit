#!/usr/bin/env bash
# Сквозной прогон конвейера МАТНОРМ через POST /api/jobs.
# Использование:
#   ./scripts/run-pipeline.sh [mode] [чертёж] [step]
#   ./scripts/run-pipeline.sh auto
#   ./scripts/run-pipeline.sh drawing_only data/drawing.png
#   ./scripts/run-pipeline.sh paired data/drawing.png data/part.step
#   BACKEND_URL=http://localhost:8123 DEBUG=true ./scripts/run-pipeline.sh auto data/drawing.png data/part.step
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://localhost:8123}"
DEBUG="${DEBUG:-false}"

# Разбор аргументов: первый токен — режим, если он известен.
MODE="auto"
DRAWING=""
STEP=""

if [[ $# -gt 0 && "$1" =~ ^(auto|drawing_only|model_only|paired)$ ]]; then
  MODE="$1"
  shift
fi

DRAWING="${1:-}"
STEP="${2:-}"

# Значения по умолчанию для smoke-теста в зависимости от режима.
if [[ -z "$DRAWING" && "$MODE" != "model_only" ]]; then
  DRAWING="$ROOT/data/drawing.png"
fi
if [[ -z "$STEP" && "$MODE" != "drawing_only" ]]; then
  STEP="$ROOT/data/part.step"
fi

URL="$BACKEND_URL/api/jobs?mode=$MODE"
[[ "$DEBUG" == "true" || "$DEBUG" == "1" ]] && URL="${URL}&debug=true"

echo "→ backend: $BACKEND_URL"
echo "→ mode:    $MODE"

CURL_ARGS=(-s -m 300)

if [[ -n "$DRAWING" && -f "$DRAWING" ]]; then
  echo "→ чертёж:  $DRAWING"
  CURL_ARGS+=(-F "drawing=@$DRAWING")
elif [[ "$MODE" == "drawing_only" || "$MODE" == "paired" ]]; then
  echo "Ошибка: чертёж не найден: ${DRAWING:-<не указан>}" >&2
  exit 1
else
  echo "→ чертёж:  (не требуется)"
fi

if [[ -n "$STEP" && -f "$STEP" ]]; then
  echo "→ STEP:    $STEP"
  CURL_ARGS+=(-F "model3d=@$STEP")
elif [[ "$MODE" == "model_only" || "$MODE" == "paired" ]]; then
  echo "Ошибка: STEP не найден: ${STEP:-<не указан>}" >&2
  exit 1
else
  echo "→ STEP:    (не требуется)"
fi

RESP=$(curl "${CURL_ARGS[@]}" "$URL")

if ! echo "$RESP" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
  echo "Ошибка ответа сервиса:" >&2
  echo "$RESP" >&2
  exit 1
fi

echo "$RESP" | python3 -m json.tool
echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ex, g = d.get('extract', {}), d.get('geometry', {})
print('--- сводка ---')
print(f\"mode={d.get('mode')} completeness={d.get('data_completeness')}\")
print(f\"extract.source={ex.get('source')} | geometry.source={g.get('source')}\")
print(f\"verify.ok={d.get('verify',{}).get('ok')} flags={len(d.get('verify',{}).get('flags',[]))}\")
print(f\"rows={len(d.get('rows',[]))} | kim={d['rows'][0].get('kim') if d.get('rows') else 'n/a'}\")
"
