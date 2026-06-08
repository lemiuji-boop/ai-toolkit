# AI-МАТНОРМ (Greenfield)

Ассистент технолога: анализ КД, КСИ, OCR/LLM, расчёт норм материалов, Excel.

## Быстрый старт

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d postgres redis minio
# дождитесь healthy у postgres, затем один раз:
cd backend && source .venv/bin/activate && python -m app.cli seed_admin
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m app.cli seed_admin
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# UI: http://127.0.0.1:5173  API: http://127.0.0.1:8001/docs
# Порт 8001 — если 8000 занят Portainer
cd ../frontend && npm install && npm run dev
```

## Стек

- Backend: FastAPI, SQLAlchemy, Alembic, RQ
- DB: PostgreSQL
- Queue: Redis + RQ worker
- Storage: MinIO
- Frontend: Vue 3 + TypeScript + Vite + Pinia
- Desktop: Tauri 2

## Проверка

```bash
./scripts/verify.sh
```

## Документация

- [ТЗ v2 (приёмка)](docs/TZ.md)
- [Трассировка FR→код→тест](docs/TRACEABILITY.md)
- [План M0–M12](docs/IMPLEMENTATION_PLAN.md)
- [Чек-лист приёмки](docs/ACCEPTANCE_CHECKLIST.md)
- [ТЗ legacy Cursor](docs/TZ_LEGACY_CURSOR.md)
- [API](docs/API_CONTRACT.md)
- [Развёртывание](docs/DEPLOYMENT.md)
- [Cursor START](CURSOR_START_HERE.md)

## Тесты

```bash
cd backend && pytest
cd frontend && npm run build
docker compose -f infra/docker-compose.yml config
```

## Не входит / database unavailable

Частая причина: том PostgreSQL от **другого** Docker-проекта (роль `ai_matnorm` не создана).

```bash
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d postgres redis minio
cd backend && source .venv/bin/activate && python -m app.cli seed_admin
```

Логин: `admin@example.com` / `admin_change_me` (из `.env`).
```
