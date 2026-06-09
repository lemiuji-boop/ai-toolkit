# Cursor — настройка для МАТНОРМ (MCC)

## 1. Открыть workspace

**Рекомендуется** — workspace только проекта (без корня монорепо):

**File → Open Workspace from File…** → `projects/MCC/mcc.code-workspace`

Альтернатива: **File → Open Folder…** → каталог `projects/MCC`.

Из корня репозитория ai-toolkit также можно открыть `matnorm-mcc.code-workspace` (одна папка — MCC).

## 2. Python

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,cad]"
```

Интерпретатор подхватится из workspace: `backend/.venv/bin/python`.

## 3. GitHub push (монорепо ai-toolkit)

Push выполняется из корня репозитория `ai-toolkit`, не из `projects/MCC`.

**Токен:** GitHub → Settings → Developer settings →
[Personal access tokens](https://github.com/settings/tokens) — scope `repo` или Contents: Read and write для `lemiuji-boop/ai-toolkit`.

```bash
mkdir -p ~/.config/ai-toolkit
chmod 600 ~/.config/ai-toolkit/github_token   # ghp_... или github_pat_...
cd /path/to/ai-toolkit
./scripts/gh-auth-push.sh main
```

## 4. Проверка

```bash
cd backend
ruff check . && mypy app && pytest -q
uvicorn app.main:app --port 8123
```

Правила агента: `.cursor/rules/*.mdc` в этом каталоге.
