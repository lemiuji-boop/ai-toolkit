# Развёртывание и подключение надстройки МАТНОРМ-XL

## On-premise: локальная сеть (по умолчанию)

Без Cloudflare tunnel — только LAN HTTPS (self-signed cert):

```bash
./scripts/start-matnorm-stack.sh
# USE_TUNNEL=0 по умолчанию; cloudflared останавливается автоматически
```

- IP сервера: `addin/lan-host.txt`
- API и add-in: `https://<LAN-IP>:8123` (единый origin `/addin/`, `/api/`)
- Сертификат: `deploy/certs/lan.{key,crt}` (`./scripts/gen-lan-cert.sh`)
- Firewall: `sudo ufw allow 8123/tcp` (если ufw активен)
- Проверка: `curl -k https://<LAN-IP>:8123/health`

Tunnel (`USE_TUNNEL=1`) — только для временной отладки вне LAN; см. `scripts/start-tunnel.sh`.

Подробные шаги для Windows — `addin/README.md`.

## Локальная проверка надстройки (без Excel-сервера)
```bash
# 1) Бэкенд (Ubuntu-хост)
cd backend && source .venv/bin/activate
uvicorn app.main:app --port 8000

# 2) Статика надстройки
cd addin && python3 -m http.server 3000
```
Открыть `http://localhost:3000/taskpane.html`. В Excel надстройка подключается
sideload'ом (см. ниже); адрес бэкенда вводится в панели и сохраняется в
`localStorage` (например `http://localhost:8000` при локальной проверке).

## Sideload в Excel (без прав администратора)
1. **Каталог надстроек.** Excel → Параметры → Центр управления безопасностью →
   Параметры центра → Каталоги надёжных надстроек → добавить сетевую папку с
   `manifest.xml` → перезапустить Excel → Вставка → Мои надстройки → Общая папка.
2. **Централизованно (M365).** Админ загружает `manifest.xml` через Integrated apps /
   Centralized Deployment и назначает пользователям.

Перед публикацией в `addin/manifest.xml` заменить:
- `Id` — на собственный GUID (`uuidgen`);
- `SourceLocation` — на реальный HTTPS-URL (Vercel или внутренний nginx).

## Продакшн: устранение mixed content (HTTPS ↔ HTTPS)
Оболочка надстройки отдаётся по HTTPS, поэтому браузер блокирует вызовы к
HTTP-бэкенду. Варианты:
- **Внутренний TLS (рекомендуется для on-premise).** Поднять nginx-терминатор
  перед бэкендом — см. `deploy/nginx-matnorm.conf`. Адрес бэкенда в панели —
  `https://matnorm.localdomain` (внутреннее DNS-имя).
- **Vercel для оболочки.** `cd addin && vercel --prod`; затем обновить
  `SourceLocation` в `manifest.xml` и сузить `CORS_ORIGINS` бэкенда до URL
  надстройки. КД через Vercel не проходят (только статика UI).

## CORS
В проде в `backend/.env` сузить `CORS_ORIGINS` до точного источника надстройки,
например `["https://your-addin.vercel.app"]`.

## Админ-панель мониторинга
Локальный UI для состояния сервисов, GPU, прогресса экспорта, RAG и последних заданий
(без обозначений изделий).

```bash
# Полный стек (backend + RAG + add-in + tunnel + admin)
./scripts/start-matnorm-stack.sh

# Только админ-панель (поднимет backend при необходимости)
chmod +x scripts/start-admin.sh
./scripts/start-admin.sh
```

- **URL панели:** `http://127.0.0.1:3010` (порт 3010: 3001 часто занят AnythingLLM)
- **API:** `GET http://127.0.0.1:8123/api/admin/…`

| Эндпойнт | Назначение |
|----------|------------|
| `/api/admin/status` | Статус сервисов (backend, RAG, Ollama, add-in, tunnel), `tunnel_url` |
| `/api/admin/progress` | Прогресс пакетного экспорта (% из `report_summary.json`) |
| `/api/admin/exports` | Список готовых файлов в `data/exports/` |
| `/api/admin/exports/download?path=…` | Скачивание (только разрешённые пути, без traversal) |
| `/api/admin/rag/overview` | Сводка RAG + описание для оператора |
| `/api/admin/metrics` | GPU, память, load average |
| `/api/admin/jobs` | Журнал заданий (job_id + хеш входа) |

**Дашборд:** строка статуса (ok/degraded/down), ссылка на tunnel, progress bar экспорта,
карточки сервисов с подсказками «Запустить», раздел «Экспорт» (CSV/MD/JSON, zip add-in),
раздел «RAG» (статус, число чанков, пробный поиск через `/api/rag/search`).

- Переменные: `BACKEND_URL`, `ADMIN_PORT`, `BACKEND_PORT`, `MATNORM_EXPORTS_DIR`
- В `backend/.env` при необходимости: `RAG_URL`, `ADDIN_URL`, `BACKEND_URL` для проб
- Аутентификация не реализована (открытый вопрос TZ §14 п.4); в проде ограничить сеть/firewall
