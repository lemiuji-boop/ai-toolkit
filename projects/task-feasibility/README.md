# MATFES — Multi-Agent Task Feasibility & Estimation System

Система анализа технических задач: маршрутизация сложности L1–L4, guardrails, оценка feasibility, прогноз токенов/стоимости и генерация техзадания в Markdown.

## Архитектура

```
User → React UI → FastAPI → SafetyShield → LangGraph
  → router → feasibility → [pivot] → cost → documentation → .md
```

## Быстрый старт

### Backend (локально)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

### Ollama (рекомендуется для L1)

```bash
docker run -d -p 11434:11434 ollama/ollama
ollama pull qwen2.5-coder:7b
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173 — запросы проксируются на API :8000.

### Docker Compose

```bash
cp .env.example .env
# Заполните CLOUD_API_KEY для L2–L4
docker compose up --build
```

- API: http://localhost:8000
- UI: http://localhost:5173
- Ollama: http://localhost:11434

## API

### Health

```bash
curl http://localhost:8000/health
```

### Analyze

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "ShopAPI",
    "task": "Создать CRUD REST API для каталога товаров с endpoints",
    "context_lines": 100
  }'
```

### Models status

```bash
curl http://localhost:8000/api/v1/models
```

## Переменные окружения

См. [`.env.example`](.env.example).

| Переменная | Описание |
|------------|----------|
| `OLLAMA_BASE_URL` | URL Ollama (по умолчанию `http://localhost:11434`) |
| `CLOUD_API_KEY` | Ключ OpenAI-совместимого API |
| `DEFAULT_MODEL_L1` | Модель Ollama, напр. `qwen2.5-coder:7b` |
| `FEASIBILITY_THRESHOLD` | Порог FI (0.7) для pivot |

## Тесты

```bash
cd backend
pytest -v
```

Тесты не требуют живого Ollama или облачных ключей (эвристические fallback).

## Структура

- `backend/app/guardrails/` — SafetyShield
- `backend/app/agents/` — LangGraph pipeline
- `backend/app/llm/` — Ollama + OpenAI-compatible
- `frontend/` — React + Vite UI

## Traceability (ТЗ → код)

| ТЗ | Модуль |
|----|--------|
| §2 Tiered routing | `agents/nodes/router.py`, `llm/router.py` |
| §3 Safety matrix | `guardrails/shield.py` |
| §4 LangGraph | `agents/graph.py` |
| §5 Token formula | `services/token_estimator.py` |
| §6 Output .md | `services/markdown_builder.py` |
