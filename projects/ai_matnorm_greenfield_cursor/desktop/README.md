# AI-МАТНОРМ Desktop (Tauri)

Windows-приложение загружает собранный Vue frontend из `frontend/dist`.

## Сборка

```bash
cd frontend && npm run build
cd ../desktop/src-tauri
cargo tauri build
```

## Настройка сервера

URL API задаётся через `VITE_API_BASE_URL` при сборке или страницу **Настройки** в web UI (`/settings`), которая пишет `localStorage.ai_matnorm_server_url`.

Синхронизация событий: API `/api/v1/sync/events`.

API-ключи ИИ-провайдеров **не** хранятся на клиенте.
