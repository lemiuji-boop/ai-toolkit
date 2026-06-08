# Развёртывание AI-МАТНОРМ

## Требования

- Docker и Docker Compose
- Python 3.12+
- Node.js 20+
- (Опционально) Ollama на хосте
- Qdrant (опционально, для RAG): `docker compose -f infra/docker-compose.yml up -d qdrant`

## Локальный запуск

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d postgres redis minio
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m app.cli seed_admin
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# worker (отдельный терминал)
python -m app.workers.run_worker

cd ../frontend && npm install && npm run dev
```

Проверка: `./scripts/verify.sh`

Логин: `admin@example.com` / `admin_change_me` (из `.env`).

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `OCR_PROVIDER` | `tesseract` (default) или `paddle` |
| `QDRANT_URL` | http://127.0.0.1:6333 |
| `EXTERNAL_LLM_ALLOWED` | `false` — не использовать внешние API (SEC-010) |

## Production

1. Reverse proxy (Nginx/Caddy) с TLS.
2. Сильные `JWT_SECRET` и `SECRETS_ENCRYPTION_KEY`.
3. `CORS_ORIGINS` только доверенные origin.
4. VPN для доступа клиентов (первый этап).
5. Сервисы: api + worker + postgres + redis + minio + qdrant.

## Backup / Restore

```bash
./scripts/backup.sh
./scripts/restore.sh <backup_archive>
```

Smoke: после backup проверить наличие архива; restore — на тестовой БД.

## Desktop (Tauri)

```bash
cd desktop/src-tauri
cargo tauri build
```

URL сервера: страница **Настройки** в UI или `localStorage.ai_matnorm_server_url`.

## UAT

См. [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) — 10+ комплектов КД.
