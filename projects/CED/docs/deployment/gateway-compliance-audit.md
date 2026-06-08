# Аудит соответствия схеме Windows-шлюз + Ubuntu Ollama

Дата: 2026-05-29

## Соответствие архитектуре

| Требование | Статус | Реализация |
|------------|--------|------------|
| PDF и UNC только на LAN-шлюзе | OK | `ai-agent` + `file_path`; PDF не отправляются на Ubuntu |
| Ollama только на Ubuntu | OK | `llm_client` → `127.0.0.1:11434` через туннель |
| Туннель без прав админа | OK | `tunnel/plink.exe`, `start-tunnel.bat` |
| PG+Redis portable на шлюзе | OK | `runtime/`, `start-runtime.bat` |
| Desktop :8000 без /api | OK | `KdCatalog.exe` → прямой API |
| Web :8080 → API :8000 | OK | `VITE_API_BASE_URL`, `start-web.bat` |
| ai-agent :8001 localhost | OK | `AI_AGENT_BASE_URL=http://127.0.0.1:8001` |
| Docker Linux не сломан | OK | `docker-compose.yml` без изменений контракта |

## Исправлено при аудите

1. **`.env` для `KdCatalogAiAgent.exe`** — `run_agent.py` ищет `.env` в родительской папке CED-Server; `start-ai-agent.bat` с `WorkingDirectory=%~dp0`.
2. **Открытие PDF в вебе** — `CatalogDashboard` использует `apiBase`, не захардкоженный `/api`.
3. **Celery Beat на шлюзе** — `run_worker.py` запускает `worker --beat` (daily health).
4. **CORS для LAN** — в `env.gateway.example` добавлен пример IP шлюза.

## Известные ограничения (не баги)

| Тема | Описание |
|------|----------|
| Бинарники PG/Redis | Не в git; скачивание вручную (`runtime/README.md`) |
| Сборка EXE | Только на Windows |
| `web_client/.env.lan` | Перед сборкой подставить IP шлюза в LAN |
| GPO блокирует exe | Whitelist или корпоративные PG/Redis в `.env` |
| `_internal` server+worker | Общий каталог PyInstaller; ai-agent — отдельная подпапка |
| LLM | Только текст уходит в Ollama; при падении туннеля — OCR/штампы работают |

## Конфликты пакетов Python

| Контекст | Решение |
|----------|---------|
| `app` backend vs ai_agent | Раздельный pytest: `backend/tests` и `ai_agent` с `pytest.ini` pythonpath=. |
| Корневой `pytest.ini` pythonpath=backend | Не запускать ai_agent тесты из корня без `-c ai_agent/pytest.ini` |

## Чеклист перед продакшеном

- [ ] Уникальные `JWT_*`, `AI_AGENT_API_KEY`
- [ ] `CORS_ORIGINS` с реальным `http://<IP-шлюза>:8080`
- [ ] `VITE_API_BASE_URL=http://<IP-шлюза>:8000` при сборке www
- [ ] `health-check.bat` + `health-check-ollama.bat`
- [ ] [acceptance-gateway-checklist.md](./acceptance-gateway-checklist.md)
