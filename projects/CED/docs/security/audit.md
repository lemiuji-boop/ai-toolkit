# Аудит безопасности CED (включая ИИ)

Дата: 2026-05-29
Объём: backend, ai_agent, web_client, desktop, Docker.

## Резюме

| Уровень | Кол-во | Комментарий |
|---------|--------|-------------|
| Критический | 2 | Path traversal (исправлено в коде) |
| Высокий | 6 | Секреты по умолчанию, ai-agent в LAN, admin/admin |
| Средний | 8 | Rate limit, refresh, upload limits, внешние ИИ |
| Низкий | 5 | CORS, Swagger, логирование |

### Развёртывание Windows-шлюз + Ollama на Ubuntu (LAN split)

| Аспект | Риск | Митигация в CED |
|--------|------|-----------------|
| PDF в интернет | Низкий при рекомендуемой схеме | `ai-agent` на шлюзе, в Ubuntu уходит только **текст** LLM-запросов |
| Туннель SSH/frp | Перехват промптов | SSH keys, не публиковать Ollama в WAN |
| Portable PG/Redis | Локальные данные на ПК шлюза | Шифрование диска (IT), физический доступ |
| Исходящий :22 | DLP | Whitelist на периметре |
| admin на шлюзе | Компрометация каталога | Смена пароля, отдельные учётки |

См. [lan-split-ai-tunnel.md](../deployment/lan-split-ai-tunnel.md), [windows-gateway-bundle.md](../deployment/windows-gateway-bundle.md).

---

## Критические (исправлено)

### 1. Произвольный путь к файлу (`/inbox/process-file`)

Любой **moderator/admin** мог передать `file_path=../../../windows/system32/...` и заставить конвейер читать произвольные файлы.

**Исправление:** `app/core/path_security.py`, проверка в `inbox.py`, `documents.py`, `document_ai.py`, `ai_agent` `/analyze`.

### 2. Path traversal при загрузке PDF

Имя файла `../../evil.pdf` записывалось в storage.

**Исправление:** `safe_upload_filename()` в `document_service.py`.

---

## Высокий риск

### 3. Учётные данные и секреты по умолчанию

- Bootstrap: **admin / admin** с флагом `must_change_password` — при первом входе обязательна смена (`/auth/change-password`)
- `.env.example`: слабые секреты — в `production` пишется CRITICAL в лог при старте

**Рекомендации:** хранить секреты в Vault; не использовать admin/admin после первого входа.

### 4. AI-agent был опубликован на порт 8001

При знании `X-API-Key` возможно чтение любого PDF в пределах томов (до патча — любого пути на диске).

**Исправление:** порт `8001` убран из `docker-compose` (только internal network).
**Рекомендации:** длинный случайный `AI_API_KEY` / `AI_AGENT_API_KEY`; ротация ключей.

### 5. Один общий ключ backend ↔ ai-agent

`internal_ai` и вызовы analyze используют один `AI_AGENT_API_KEY`. Компрометация ключа = полный доступ к анализу и метаданным провайдеров.

**Рекомендации:** отдельные ключи для internal / agent; mTLS между сервисами в production.

### 6. Внешние ИИ-провайдеры (`allow_external_providers`)

При включении PDF/текст уходит на `base_url` внешнего провайдера (Ollama в LAN или облако). Риск утечки КД и извещений.

**Рекомендации:** по умолчанию только local; DLP-политика; журнал отправок; air-gap для секретных контуров.

### 7. Нет ограничения частоты (rate limiting)

**Исправлено:** Redis — 5 неудачных попыток / 15 мин на пару IP+login (`rate_limit_service.py`).

### 8. Refresh token без отзыва и rotation

Refresh валиден до истечения срока; украденный refresh = долгий доступ.

**Рекомендации:** refresh rotation, blacklist в Redis, привязка к device id.

---

## Средний риск

### 9. ИИ-чат каталога (`/catalog/chat`)

Сейчас **не LLM**, а regex-фильтры — риск prompt injection низкий. При подключении LLM:

- не передавать сырой системный промпт от пользователя без sandbox;
- ограничить tools (только filter, не SQL);
- не отдавать пути за пределы прав пользователя.

### 10. Утечка путей UNC в ответах чата

Аутентифицированный пользователь получает `\\server\share\...` — приемлемо внутри контура, риск при компрометации клиента.

### 11. Роль `user` — чтение всех документов

Любой авторизованный пользователь: каталог, скачивание PDF, analyze/validate.

**Рекомендации:** ABAC по подразделению (`department`), если нужна изоляция цехов.

### 12. Загрузка без лимита размера

**Исправлено:** `MAX_UPLOAD_BYTES` (100 МБ по умолчанию), nginx `client_max_body_size 100m`.

### 13. Swagger в debug

`docs_url` открыт при `DEBUG=true`.

**Рекомендации:** `DEBUG=false` в production; docs только на admin VPN.

### 14. Fernet для ключей провайдеров

Ключ из `AI_FERNET_KEY` с усечением до 32 байт — слабее, чем полноценный `Fernet.generate_key()`.

**Рекомендации:** генерировать ключ `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.

### 15. Сообщения об ошибках ИИ в system_messages

Текст исключений может попасть админам — возможна утечка внутренних путей. Уже частично ограничено; обрезать stack traces в production.

### 16. PDF parsing (pdfplumber)

Вредоносный PDF → риски parser bomb / CVE в зависимостях.

**Рекомендации:** обновлять зависимости; обрабатывать в изолированном worker; лимит страниц/размера.

---

## Низкий риск

### 17. CORS

Список origin ограничен; при неправильном nginx возможен лишний origin.

### 18. JWT в localStorage (web)

Уязвимость к XSS. **Рекомендации:** httpOnly cookies + CSRF token при переходе на browser-only.

### 19. Desktop хранит токены в config / памяти

Компрометация ПК = доступ к API.

### 20. Отсутствие аудита на скачивание файлов

`GET /documents/{id}/file` не пишет в `Log` — сложнее расследование.

### 21. Postgres/Redis без TLS в docker-compose

Внутри compose OK; в production — TLS и пароли.

---

## Модель угроз «против ИИ»

| Угроза | Текущее состояние | Меры |
|--------|-------------------|------|
| Prompt injection в чат | Нет LLM | При добавлении LLM — system prompt + allowlist tools |
| Exfiltration через внешний API | Возможно при external provider | Только local Ollama; сеть egress firewall |
| Подмена ответа ИИ (MITM) | httpx без verify pin | HTTPS + private network |
| Отравление INBOX (ложный PDF) | Есть confidence threshold | Ручной разбор; AV scan |
| Злоупотребление analyze API | Нужен JWT + path allowlist | Патч path_security |
| Model poisoning (Ollama) | Зависит от инфраструктуры | Контроль образов, pull только доверенных моделей |
| Утечка чертежей в логи Celery | Логи могут содержать пути | Маскирование в production logging |

---

## Чек-лист перед production

- [ ] Сменить все секреты в `.env` (JWT, AI keys, Fernet, Postgres)
- [ ] Сменить пароль admin, отключить автосоздание слабого пароля
- [ ] `DEBUG=false`, закрыть Swagger
- [ ] ai-agent не в public ports
- [ ] TLS (nginx), firewall только 443/80
- [ ] Rate limit на login
- [ ] Backup БД, шифрование диска на сервере каталога
- [ ] Политика: внешние ИИ-провайдеры запрещены без письменного разрешения
- [ ] Регулярное `pip audit` / Dependabot

---

## Внесённые изменения (код)

- `backend/app/core/path_security.py`
- `ai_agent/app/core/path_security.py`
- Проверки в upload, download, inbox, document_ai, analyze
- `docker-compose`: ai-agent без публикации порта 8001, общие volumes catalog/storage
