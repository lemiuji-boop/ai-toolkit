# RAG-сервис нормативов (СЕРВИС-05)

On-premise семантический поиск по нормативной базе (ГОСТ/ОСТ/ТУ, rules.json, docs).
Эмбеддинги — **только локальный Ollama** (`nomic-embed-text`) с деградацией к stub.

## Эндпойнты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Статус сервиса |
| GET | `/version` | Версия, бэкенд Chroma, модель эмбеддингов |
| POST | `/index` | Прямая индексация документов (FR-001) |
| POST | `/ingest` | Загрузка из PDF/MD/JSON по путям |
| POST | `/search` | Семантический поиск с `source` (FR-002/003) |

Порт по умолчанию: **8020**.

## Быстрый старт

```bash
# из корня projects/MCC
./scripts/start-rag.sh
```

Или вручную:

```bash
cd services/rag
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export PROJECT_ROOT=/path/to/projects/MCC
export CHROMA_PATH=$PROJECT_ROOT/data/rag/chroma
export OLLAMA_URL=http://127.0.0.1:11434
uvicorn app.main:app --host 127.0.0.1 --port 8020
```

Ollama (эмбеддинги):

```bash
ollama pull nomic-embed-text
```

## Ingest

Автокорпус при первом старте (пустой индекс):

- `backend/app/data/rules.json` (санitized)
- `docs/TZ.md`
- `data/rag/*.md`

```bash
curl -X POST http://127.0.0.1:8020/ingest \
  -H 'Content-Type: application/json' \
  -d '{"use_default_corpus": true, "reindex": false}'
```

Явные пути:

```bash
curl -X POST http://127.0.0.1:8020/ingest \
  -H 'Content-Type: application/json' \
  -d '{"paths": ["data/rag/normatives-overview.md"], "use_default_corpus": false}'
```

PDF из конфиденциальных каталогов **не** индексируются без явного указания пути.

## Search

```bash
curl -X POST http://127.0.0.1:8020/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "припуски на поковки", "top_k": 5}'
```

## Интеграция с backend

- Проба здоровья: `admin_monitor.probe_rag()` → `GET :8020/health`
- Прокси (§14 ТЗ): `POST /api/rag/search` → RAG `:8020/search`
- Клиент: `backend/app/services/rag_client.py`

## Конфигурация

См. `.env.example`: `CHROMA_PATH`, `OLLAMA_URL`, `EMBED_MODEL`, `EMBED_BACKEND` (`auto`|`ollama`|`stub`).

Persistent ChromaDB: `data/rag/chroma/`.

## Тесты

```bash
cd services/rag
ruff check .
pytest -q
```

Тесты используют `CHROMA_PATH=memory` и `EMBED_BACKEND=stub` (без Ollama).

## Docker

```bash
docker compose up rag --build
```

## Чанкинг

Русскоязычные технические тексты: разбиение по абзацам и заголовкам markdown,
склейка до `CHUNK_SIZE` (800), перекрытие `CHUNK_OVERLAP` (120).

## Stub vs production

| Компонент | Stub (тесты/деградация) | Production |
|-----------|-------------------------|------------|
| Эмбеддинги | MD5 bag-of-words | Ollama `nomic-embed-text` |
| ChromaDB | in-memory (`CHROMA_PATH=memory`) | `data/rag/chroma/` |
| Корпус | seed (5 записей) | seed + rules.json + TZ.md + data/rag |
