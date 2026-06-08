# API Mobile НТИ.Сбор v1

Base path: `/api/v1`

Аутентификация: `Authorization: Bearer <access_token>` (после входа) или dev-токен `dev-device-token`.

## Вход пользователя

```http
POST /mobile/auth/login
Content-Type: application/json

{ "username": "ivanov", "password": "demo123" }
```

Ответ: `{ "access_token": "...", "display_name": "...", "tab_number": "1001" }`

Демо-учётки: `ivanov` / `petrov`, пароль `demo123`.

```http
GET /mobile/auth/me
POST /mobile/auth/logout
```

## Health

```http
GET /health
```

Ответ: `{ "status": "ok" }`

## Справочник операций (FR-014)

```http
GET /mobile/operations
```

Ответ: `[{ "id": 1, "name": "Токарная", "active": true }]`

## Пакетная отправка записей (FR-013)

```http
POST /mobile/labor-records/batch
Content-Type: application/json
```

Тело:

```json
{
  "records": [
    {
      "client_id": "uuid",
      "date": "2026-06-04",
      "worker": "Иванов И.И.",
      "product": "З-100",
      "operation": "Токарная",
      "value": 1.5,
      "unit": "н/ч",
      "note": ""
    }
  ]
}
```

Ответ:

```json
{
  "accepted": [{ "client_id": "uuid", "server_id": "srv-1" }],
  "errors": []
}
```

Идемпотентность: повторная отправка с тем же `client_id` не создаёт дубликат.

## Безопасность

- Только HTTPS (TLS 1.2+), cleartext запрещён.
- Токен устройства выдаётся администратором НТИ.
