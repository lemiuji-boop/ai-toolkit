# МАТНОРМ — каркас системы (vertical slice)

Работающий не на полную мощность каркас, готовый к подключению полных модулей.
Минимум, который уже работает: распознавание чертежа → сопоставление с 3D →
детерминированный расчёт норм → перенос и нормоконтроль в Excel.

## Состав
- `backend/` — FastAPI на Ubuntu-хосте: модули vision (LLM-клиент + OCR-препроцессор),
  geometry (STEP через cadquery с заглушкой, дерево изделия), verify, calc (правила и
  виды заготовки в `app/data/rules.json`, входимость на с/к), excel_format. Каждый
  модуль заменяется полным без правок API.
- `services/rag/` — RAG-сервис нормативов (СЕРВИС-05): индексация и поиск по
  ГОСТ/ОСТ/ТУ с цитированием источника (ChromaDB).
- `addin/` — Office-надстройка (Office.js) для Excel, хостится на Vercel/nginx.
- `docs/` — ТЗ (`TZ.md`), трассировка FR→тест (`trace.md`), рабочий контекст.
- `.cursor/rules/`, `CLAUDE.md`, `AGENTS.md` — правила для AI-агентов разработки.
- `deploy/` — TLS reverse-proxy (nginx) и инструкция подключения надстройки.
- `docker-compose.yml` — backend + rag + (опционально, профиль `gpu`) inference.

## Где что крутится
| Компонент | Где | Видит ли КД |
|---|---|---|
| Бэкенд + LLM + 3D + расчёт | Ubuntu-ПК (этот) | да (локально) |
| Веб-оболочка надстройки | Vercel (облако) | нет — только UI-код |
| Excel пользователя | Windows, без прав админа | да (между Excel и бэкендом) |

КД не проходит через Vercel: оболочка лишь раздаётся как статика, данные идут
напрямую Excel ↔ Ubuntu-бэкенд по внутренней сети.

## Запуск бэкенда (Ubuntu-хост)
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,cad]"      # cad тянет cadquery/OCP (numpy<2 закреплён)
uvicorn app.main:app --reload --port 8000
ruff check . && mypy app && pytest -q   # все проверки зелёные
```
Без модели/без 3D каркас всё равно отрабатывает (заглушки помечены `source=stub`).

### Контейнеры
Имя каталога кириллическое, поэтому compose-проекту задаём имя явно (`-p matnorm`).
По умолчанию бэкенд ходит в Ollama на хосте (`host.docker.internal:11434`);
контейнер inference с GPU — опциональный профиль `gpu`.
```bash
docker compose -p matnorm up --build -d            # backend + rag
# host-порт backend настраивается: BACKEND_PORT=8001 docker compose -p matnorm up -d
# inference отдельным GPU-контейнером (узел >= 16 ГБ):
docker compose -p matnorm --profile gpu up -d inference
docker compose -p matnorm exec inference ollama pull qwen3-vl:8b   # тег уточнить
```

## RAG-сервис нормативов (СЕРВИС-05)
```bash
cd services/rag && python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && pytest -q
uvicorn app.main:app --port 8020
curl -s -X POST localhost:8020/search -H 'Content-Type: application/json' \
  -d '{"query":"припуски на поковки","top_k":3}'
```

## Деплой надстройки и подключение пользователей
См. `deploy/README.md` (локальный sideload, TLS против mixed content) и
`addin/README.md` (Vercel + раздача без прав админа).

## Что осталось «недоделанным» (намеренно, под полную систему)
- vision — реальная дообученная Qwen3-VL вместо заглушки; полноценный OCR (PaddleOCR);
- geometry — NX/CATIA и чтение дерева сборки из STEP (XCAF) помимо одиночной детали;
- шлюз-страж, внешний оркестратор, downstream-API (СЕРВИС-08/09/11).
См. `ARCHITECTURE.md`, `docs/TZ.md` и пакеты документов 00–02.
