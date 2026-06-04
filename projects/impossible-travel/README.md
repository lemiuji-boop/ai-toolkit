# Impossible Travel AI Blog

AI-студия для фотореалистичного виртуального тревел-блога о невозможных местах. MVP работает на mock-провайдерах; архитектура готова к подключению реальных API.

## Стек

- **Frontend:** Next.js, TypeScript, Tailwind, shadcn/ui
- **Backend:** FastAPI, SQLAlchemy, Alembic, Celery
- **Infra:** PostgreSQL (pgvector), Redis, MinIO

## Быстрый старт

```bash
# 1. Инфраструктура
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d

# 2. Backend
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Celery worker (отдельный терминал)
cd /path/to/Travel_AI
source services/api/.venv/bin/activate
export PYTHONPATH=services/api
celery -A apps.worker.celery_app worker --loglevel=info

# 4. Frontend
npm install
npm run dev:web
```

- API: http://localhost:8000/docs
- Web: http://localhost:3000
- MinIO Console: http://localhost:9001 (minio / minio123)

## MVP User Flow

1. Откройте `/episodes/new`
2. Введите тему, например «жерло вулкана»
3. Нажмите «Сгенерировать»
4. Дождитесь статуса `ready_for_review`
5. Просмотрите вкладки и нажмите «Утвердить»

## Структура

```text
Travel_AI/
├── apps/web/          # Next.js dashboard
├── apps/worker/       # Celery worker
├── services/api/      # FastAPI + agents
├── infra/             # docker-compose
└── docs/              # спецификация и агенты
```

## Документация

- [PROJECT_SPEC.md](docs/PROJECT_SPEC.md)
- [AGENTS.md](docs/AGENTS.md)
- [PROMPT_LIBRARY.md](docs/PROMPT_LIBRARY.md)
- [ROADMAP.md](docs/ROADMAP.md)
