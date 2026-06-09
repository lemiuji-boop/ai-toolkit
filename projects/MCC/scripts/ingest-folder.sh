#!/usr/bin/env bash
# Сканирование папки с КД: автодетект пар по базовому имени, запуск конвейера.
# Использование:
#   ./scripts/ingest-folder.sh /path/to/folder
#   ./scripts/ingest-folder.sh data/incoming/pairs
#   DRY_RUN=1 ./scripts/ingest-folder.sh data/incoming/drawings
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FOLDER="${1:-}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8123}"
DEBUG="${DEBUG:-false}"
DRY_RUN="${DRY_RUN:-false}"

if [[ -z "$FOLDER" || ! -d "$FOLDER" ]]; then
  echo "Использование: $0 /path/to/folder" >&2
  exit 1
fi

# Собираем файлы по расширениям (без учёта регистра).
mapfile -t DRAWINGS < <(find "$FOLDER" -maxdepth 1 -type f \( \
  -iname '*.pdf' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) | sort)
mapfile -t MODELS < <(find "$FOLDER" -maxdepth 1 -type f \( \
  -iname '*.step' -o -iname '*.stp' \) | sort)

# Базовое имя без расширения (нижний регистр).
basename_key() {
  local f="$1"
  local name
  name="$(basename "$f")"
  echo "${name%.*}" | tr '[:upper:]' '[:lower:]'
}

declare -A DRAW_BY_KEY MODEL_BY_KEY
for f in "${DRAWINGS[@]}"; do
  DRAW_BY_KEY["$(basename_key "$f")"]="$f"
done
for f in "${MODELS[@]}"; do
  MODEL_BY_KEY["$(basename_key "$f")"]="$f"
done

# Ключи пар: пересечение имён.
PAIRED_KEYS=()
DRAW_ONLY_KEYS=()
MODEL_ONLY_KEYS=()

for key in "${!DRAW_BY_KEY[@]}"; do
  if [[ -n "${MODEL_BY_KEY[$key]:-}" ]]; then
    PAIRED_KEYS+=("$key")
  else
    DRAW_ONLY_KEYS+=("$key")
  fi
done
for key in "${!MODEL_BY_KEY[@]}"; do
  if [[ -z "${DRAW_BY_KEY[$key]:-}" ]]; then
    MODEL_ONLY_KEYS+=("$key")
  fi
done

echo "→ папка: $FOLDER"
echo "→ пар: ${#PAIRED_KEYS[@]}, только чертежи: ${#DRAW_ONLY_KEYS[@]}, только 3D: ${#MODEL_ONLY_KEYS[@]}"

run_job() {
  local mode="$1"
  local draw="${2:-}"
  local step="${3:-}"
  echo ""
  echo "=== $mode: ${draw:-—} + ${step:-—} ==="
  if [[ "$DRY_RUN" == "true" || "$DRY_RUN" == "1" ]]; then
    echo "(dry-run, пропуск curl)"
    return
  fi
  local args=("$ROOT/scripts/run-pipeline.sh" "$mode")
  [[ -n "$draw" ]] && args+=("$draw")
  [[ -n "$step" ]] && args+=("$step")
  BACKEND_URL="$BACKEND_URL" DEBUG="$DEBUG" "${args[@]}"
}

for key in "${PAIRED_KEYS[@]}"; do
  run_job paired "${DRAW_BY_KEY[$key]}" "${MODEL_BY_KEY[$key]}"
done
for key in "${DRAW_ONLY_KEYS[@]}"; do
  run_job drawing_only "${DRAW_BY_KEY[$key]}"
done
for key in "${MODEL_ONLY_KEYS[@]}"; do
  run_job model_only "" "${MODEL_BY_KEY[$key]}"
done

if [[ ${#PAIRED_KEYS[@]} -eq 0 && ${#DRAW_ONLY_KEYS[@]} -eq 0 && ${#MODEL_ONLY_KEYS[@]} -eq 0 ]]; then
  echo "В папке не найдено PDF/PNG/JPG или STEP/STP файлов." >&2
  exit 1
fi
