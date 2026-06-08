# Traceability Matrix (CURSOR_LAUNCH + CURSOR_ДОРАБОТКА)

| # | Критерий | Реализация | Статус |
|---|----------|------------|--------|
| 1-8 | Базовый CURSOR_LAUNCH | backend/api, ai_agent, docker, web, desktop | implemented |
| 9 | Права на папку | `storage_access.py` write-probe | implemented |
| 10 | INBOX-конвейер | watcher + Celery + `/inbox/*` | implemented |
| 11 | OCR КД/ИИ | `stamp_kd.py`, `stamp_ii.py`, `runner.py` | implemented |
| 12 | Множественные директивы | `change_order_directives`, ingest II | implemented |
| 13 | Навигация КД↔ИИ | change-orders + catalog API | implemented |
| 14 | Роли | admin/moderator/user + `require_mutation_access` | implemented |
| 15 | История редакций | `record_revisions` + `/records/.../history` | implemented |
| 16 | Excel export | `/catalog/export` + строки директив ИИ | implemented |
| 17 | Portable EXE | server/client config, forms, portable.md | implemented |
| 18 | Локальные провайдеры | bootstrap Ollama + settings flag | implemented |
| 19 | LAN split: Windows gateway + tunnel | `build/windows/*`, `windows-gateway-bundle.md`, `llm_client.py` | implemented |
| UI | Референс CD & AI Catalog | `CatalogDashboard.vue`, `AppShell.vue`, WinForms layout | implemented |

## Учётные данные по умолчанию

- login: `admin`
- password: `admin` (сменить после первого входа)

## Проверка

```bash
bash scripts/setup_dev.sh   # .env, venv, web dist
bash scripts/run_all_tests.sh
docker compose up --build
cd ../web_client && npm install && npm run build
docker compose up --build
```
