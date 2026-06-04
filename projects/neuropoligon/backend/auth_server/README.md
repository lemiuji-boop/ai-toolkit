# Backend авторизации Нейрополигон

## Запуск

```bash
cd backend/auth_server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export JWT_SECRET="ваш-секрет"
export ADMIN_EMAIL="admin@example.com"   # только этот email получит role=admin
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your@gmail.com"
export SMTP_PASSWORD="app-password"
export SMTP_FROM="your@gmail.com"
uvicorn main:app --host 0.0.0.0 --port 8080
```

Без SMTP код печатается в консоль сервера (режим разработки).

## Android

- Эмулятор: `http://10.0.2.2:8080` (уже в `DEFAULT_AUTH_API_BASE_URL`)
- Телефон в Wi‑Fi: `http://IP_ВАШЕГО_ПК:8080` — сохраните в secure storage через будущую настройку или поменяйте константу в `AuthConfig.kt`

## Админ

Откройте `admin_web/index.html` в браузере, укажите URL backend и войдите под `ADMIN_EMAIL`.
В Android-приложении вход с `role=admin` **заблокирован**.
