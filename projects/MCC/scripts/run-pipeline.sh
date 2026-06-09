#!/usr/bin/env bash
# Сквозной прогон конвейера МАТНОРМ через POST /api/jobs.
# Использование:
#   ./scripts/run-pipeline.sh --drawing data/drawing.png
#   ./scripts/run-pipeline.sh --model data/part.step
#   ./scripts/run-pipeline.sh --drawing a.pdf --model a.step
#   ./scripts/run-pipeline.sh --folder data/incoming/pairs
#   ./scripts/run-pipeline.sh --mode paired --drawing a.png --model a.step
#   BACKEND_URL=http://localhost:8123 DEBUG=true ./scripts/run-pipeline.sh --drawing data/drawing.png
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://localhost:8123}"
DEBUG="${DEBUG:-false}"

MODE="auto"
DRAWING=""
STEP=""
FOLDER=""

usage() {
  cat <<EOF
Использование: $0 [опции]

  --mode MODE       auto|drawing_only|model_only|paired (по умолчанию auto)
  --drawing PATH    чертёж (PDF/PNG/JPG)
  --model PATH      3D-модель (STEP/STP)
  --folder PATH     папка с КД → делегирует ingest-folder.sh

Хотя бы один из --drawing, --model или --folder обязателен.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:?}"
      shift 2
      ;;
    --drawing)
      DRAWING="${2:?}"
      shift 2
      ;;
    --model)
      STEP="${2:?}"
      shift 2
      ;;
    --folder)
      FOLDER="${2:?}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Неизвестный аргумент: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -n "$FOLDER" ]]; then
  exec "$ROOT/scripts/ingest-folder.sh" "$FOLDER"
fi

if [[ -z "$DRAWING" && -z "$STEP" ]]; then
  echo "Ошибка: укажите --drawing, --model или --folder" >&2
  usage >&2
  exit 1
fi

URL="$BACKEND_URL/api/jobs?mode=$MODE"
[[ "$DEBUG" == "true" || "$DEBUG" == "1" ]] && URL="${URL}&debug=true"

echo "→ backend: $BACKEND_URL"
echo "→ mode:    $MODE"

CURL_ARGS=(-s -m 300)

if [[ -n "$DRAWING" ]]; then
  if [[ ! -f "$DRAWING" ]]; then
    echo "Ошибка: чертёж не найден: $DRAWING" >&2
    exit 1
  fi
  echo "→ чертёж:  $DRAWING"
  CURL_ARGS+=(-F "drawing=@$DRAWING")
else
  echo "→ чертёж:  (не указан)"
fi

if [[ -n "$STEP" ]]; then
  if [[ ! -f "$STEP" ]]; then
    echo "Ошибка: STEP не найден: $STEP" >&2
    exit 1
  fi
  echo "→ STEP:    $STEP"
  CURL_ARGS+=(-F "model3d=@$STEP")
else
  echo "→ STEP:    (не указан)"
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
