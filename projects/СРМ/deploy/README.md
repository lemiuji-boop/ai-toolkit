# Развёртывание и подключение надстройки МАТНОРМ-XL

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
