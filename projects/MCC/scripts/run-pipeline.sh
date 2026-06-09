#!/usr/bin/env bash
# Сквозной прогон конвейера МАТНОРМ через POST /api/jobs.
# Использование:
#   ./scripts/run-pipeline.sh [чертёж] [step]
#   ./scripts/run-pipeline.sh /path/to/drawing.pdf /path/to/part.step
#   BACKEND_URL=http://localhost:8123 ./scripts/run-pipeline.sh data/incoming/foo.png data/incoming/foo.step
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_URL="${BACKEND_URL:-http://localhost:8123}"
DRAWING="${1:-$ROOT/data/drawing.png}"
STEP="${2:-$ROOT/data/part.step}"
DEBUG="${DEBUG:-false}"

if [[ ! -f "$DRAWING" ]]; then
  echo "Ошибка: чертёж не найден: $DRAWING" >&2
  exit 1
fi

URL="$BACKEND_URL/api/jobs"
[[ "$DEBUG" == "true" || "$DEBUG" == "1" ]] && URL="${URL}?debug=true"

echo "→ backend: $BACKEND_URL"
echo "→ чертёж:  $DRAWING"
if [[ -f "$STEP" ]]; then
  echo "→ STEP:    $STEP"
  RESP=$(curl -s -m 300 -F "drawing=@$DRAWING" -F "model3d=@$STEP" "$URL")
else
  echo "→ STEP:    (нет файла, только чертёж)"
  RESP=$(curl -s -m 300 -F "drawing=@$DRAWING" "$URL")
fi

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
print(f\"extract.source={ex.get('source')} | geometry.source={g.get('source')}\")
print(f\"verify.ok={d.get('verify',{}).get('ok')} flags={len(d.get('verify',{}).get('flags',[]))}\")
print(f\"rows={len(d.get('rows',[]))} | kim={d['rows'][0].get('kim') if d.get('rows') else 'n/a'}\")
"
