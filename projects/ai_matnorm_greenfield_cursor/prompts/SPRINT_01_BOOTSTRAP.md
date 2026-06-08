# Sprint 01: Bootstrap whole stack

## Goal

Create initial runnable monorepo for AI-МАТНОРМ.

## Backend

Create FastAPI app with:

- `/api/v1/health` endpoint;
- settings from env;
- structured logging;
- pytest test for health;
- clean module structure.

## Frontend

Create Vue 3 + TypeScript + Vite app with:

- dashboard placeholder;
- API health check card;
- basic routing placeholder;
- theme foundation.

## Infrastructure

Create Docker compose with:

- postgres;
- redis;
- minio;
- backend placeholder service;
- frontend placeholder service optional.

## Acceptance

```bash
cd backend
pytest

cd ../frontend
npm run build

docker compose -f infra/docker-compose.yml config
```

Do not implement auth yet. Auth is Sprint 02.
