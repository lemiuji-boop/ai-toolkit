# Приёмочный чеклист: Windows-шлюз + туннель Ollama

Отмечайте `[x]` при успешном прохождении на стенде.

## A. Подготовка Ubuntu (внешняя)

- [ ] A1. Ollama установлен, `ollama pull qwen2.5-coder`
- [ ] A2. Ollama слушает `127.0.0.1:11434`
- [ ] A3. Пользователь `cedtunnel`, ключ SSH в `authorized_keys`
- [ ] A4. С хоста Ubuntu: `curl http://127.0.0.1:11434/api/tags` → OK

## B. Подготовка Windows-шлюза (без админа)

- [ ] B1. Папка `CED-Server` в профиле пользователя
- [ ] B2. `runtime\` заполнен по `runtime/README.md`
- [ ] B3. `init-runtime.bat` завершился без ошибок
- [ ] B4. `tunnel\plink.exe` + `tunnel.env`, `setup-tunnel.bat`
- [ ] B5. `.env` из `env.gateway.example`, `CATALOG_ROOT` = UNC
- [ ] B6. Доступ на запись в `\\FILESRV\...\KDCatalog\_INBOX`

## C. Запуск стека

- [ ] C1. `start-server.bat` — окна tunnel, API, worker, ai-agent без падения
- [ ] C2. `health-check.bat` → `/health` OK
- [ ] C3. `health-check-ollama.bat` → OK
- [ ] C4. `http://127.0.0.1:8000/docs` открывается (если DEBUG)
- [ ] C5. `http://127.0.0.1:8080` — веб-логин

## D. Безопасность и учётки

- [ ] D1. Вход `admin`/`admin` → принудительная смена пароля
- [ ] D2. JWT не из `.env.example` в production
- [ ] D3. После 5 неверных логинов — блокировка (rate limit)

## E. Каталог и INBOX

- [ ] E1. PDF в `_INBOX` обработан (файл в `catalog` или pending)
- [ ] E2. Запись видна в API `/catalog`
- [ ] E3. Повторная загрузка того же hash — dedup/пропуск по логике

## F. Desktop-клиент

- [ ] F1. `KdCatalog.exe`, режим `client`, `http://<шлюз>:8000`
- [ ] F2. Поиск и карточка документа
- [ ] F3. `config.json` в `%APPDATA%\KdCatalog\`

## G. Веб-модератор

- [ ] G1. Логин на `http://<шлюз>:8080`
- [ ] G2. Раздел пользователей (роль admin/moderator)
- [ ] G3. Загрузка PDF (admin upload)
- [ ] G4. Мониторинг — статусы сервисов

## H. ИИ и туннель

- [ ] H1. Анализ документа с туннелем — поля KD заполнены
- [ ] H2. Остановка туннеля — анализ без LLM, без падения API
- [ ] H3. Восстановление туннеля — LLM снова доступен
- [ ] H4. PDF не передаётся на Ubuntu (проверка трафика/логов)

## I. Остановка

- [ ] I1. `stop-server.bat` завершает процессы
- [ ] I2. Повторный `start-server.bat` — стек поднимается

## J. Нагрузка (опционально)

- [ ] J1. 10 параллельных логинов — без 500
- [ ] J2. INBOX 20 файлов — очередь Celery обрабатывает

**Итого:** ___ / 32 обязательных (J — опционально).
