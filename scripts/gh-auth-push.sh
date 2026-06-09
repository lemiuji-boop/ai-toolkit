#!/usr/bin/env bash
# Авторизация GitHub и push для ai-toolkit.
# Требуется PAT с правом Contents: Read and write (classic: scope repo,
# или fine-grained: Repository contents → Read and write для lemiuji-boop/ai-toolkit).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="${GITHUB_TOKEN_FILE:-$HOME/.config/ai-toolkit/github_token}"

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  TOKEN="$GITHUB_TOKEN"
elif [[ -f "$TOKEN_FILE" ]]; then
  TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"
else
  echo "Нет токена. Варианты:" >&2
  echo "  1) export GITHUB_TOKEN=ghp_..." >&2
  echo "  2) mkdir -p ~/.config/ai-toolkit && echo 'ghp_...' > $TOKEN_FILE && chmod 600 $TOKEN_FILE" >&2
  echo "  3) gh auth login -h github.com -s repo" >&2
  exit 1
fi

echo "$TOKEN" | gh auth login --with-token
gh auth setup-git

cd "$REPO_ROOT"
branch="${1:-main}"
echo "→ push origin $branch"
git push origin "$branch"
