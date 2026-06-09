# Cursor — настройка для МАТНОРМ (projects/MCC)

## 1. Открыть правильный workspace

В Cursor: **File → Open Workspace from File…** → выбрать в корне репозитория:

`ai-toolkit/matnorm-mcc.code-workspace`

Будут две папки: **МАТНОРМ (MCC)** (основная) и корень **ai-toolkit**.

## 2. Python

```bash
cd projects/MCC/backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,cad]"
```

Интерпретатор подхватится из workspace: `backend/.venv/bin/python`.

## 3. GitHub push (исправление 403)

Текущий fine-grained PAT без **Contents: write** не может пушить.

**Создать токен:** GitHub → Settings → Developer settings →
[Personal access tokens](https://github.com/settings/tokens)

- **Classic:** scope `repo`, или
- **Fine-grained:** репозиторий `lemiuji-boop/ai-toolkit`, permission **Contents: Read and write**

**Сохранить локально (не коммитить):**

```bash
mkdir -p ~/.config/ai-toolkit
chmod 700 ~/.config/ai-toolkit
nano ~/.config/ai-toolkit/github_token   # вставить ghp_... или github_pat_...
chmod 600 ~/.config/ai-toolkit/github_token
```

**Push из корня ai-toolkit:**

```bash
cd /path/to/ai-toolkit
chmod +x scripts/gh-auth-push.sh
./scripts/gh-auth-push.sh main
```

Или одной строкой: `export GITHUB_TOKEN=ghp_... && ./scripts/gh-auth-push.sh`

## 4. Проверка

```bash
cd projects/MCC/backend
ruff check . && mypy app && pytest -q
uvicorn app.main:app --port 8123
```

Правила агента: `projects/MCC/.cursor/rules/*.mdc` и корневой `.cursor/rules/00-ai-toolkit-monorepo.mdc`.
