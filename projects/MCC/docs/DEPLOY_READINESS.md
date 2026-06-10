# Готовность к тестовому развёртыванию МАТНОРМ

Дата аудита: 2026-06-10. Хост: Ubuntu, LAN IP сервера `192.168.248.202`.

## 1. Результаты проверок

| Проверка | Результат |
|---|---|
| `ruff check .` (backend) | ✓ без замечаний |
| `mypy app` (backend) | ✓ 39 файлов, без ошибок |
| `pytest -q` (backend) | ✓ **85 passed** (70 прежних + 15 новых) |
| `pytest -q` (services/rag) | ✓ 6 passed |
| `scripts/ci-stub-gate.sh` | ✓ OK |
| `scripts/preflight.sh` | ✓ все проверки пройдены |
| `docker compose -p matnorm config` | ✓ конфигурация валидна |
| `docker compose -p matnorm build` | ✓ образы `matnorm-backend`, `matnorm-rag` собраны |

## 2. Состояние git (НЕ закоммичено — ждёт обновления PAT)

Ветка `main`, **4 незапушенных коммита**:

```
ce8d9bd feat(MCC): гибкая загрузка — чертёж / модель / пара
37f3133 feat(MCC): гибкая загрузка данных
26a2ec6 chore: workspace MCC-only
d0250a4 refactor: переименовать projects/СРМ → projects/MCC
```

Незакоммиченной работы — ~95 файлов (изменённые + новые), в т.ч.:

- **изменены**: addin/* (LAN HTTPS), backend (async jobs, config, calc, vision,
  geometry), docker-compose.yml, services/rag/*, docs/TZ.md, trace.md;
- **новые**: admin/ (панель), backend/app/api/{addin,admin,rag}.py,
  app/core/crypto.py, app/db/, app/services/llm/ (router/registry/providers),
  app/services/{providers_store,clients_monitor,admin_*,job_store,...}.py,
  scripts/* (stack, cert, preflight, addin, stub-gate), docs/TZ-FINAL.md,
  deploy/certs/ (в .gitignore — ключи не коммитятся);
- **эта итерация**: CRUD провайдеров ИИ + мониторинг подключений + тесты +
  docker-compose v2 + preflight.sh + данная сводка.

Рекомендуемые коммиты после обновления PAT: один коммит «T-08: провайдеры ИИ +
мониторинг подключений + деплой-аудит» либо по задачам T-NN.
**Push:** `scripts/gh-auth-push.sh` — нужен свежий PAT (Contents: write).

## 3. Хост-стек (Cursor env) — ЗАПУЩЕН и проверен

| Сервис | URL | Статус |
|---|---|---|
| Backend (HTTPS, LAN) | `https://192.168.248.202:8123` | ✓ health ok |
| Add-in статика | `https://192.168.248.202:8123/addin/taskpane.html` | ✓ 200 |
| RAG | `http://192.168.248.202:8020` | ✓ health ok (embed: ollama:nomic-embed-text) |
| Админ-панель | `http://192.168.248.202:3010/` | ✓ 200, новые секции на месте |
| Ollama (хост) | `http://127.0.0.1:11434` | ✓ 9 моделей, qwen3-vl:8b-instruct установлена |

Перезапуск (идемпотентный): `./scripts/start-matnorm-stack.sh`
(с новым кодом — `FORCE_RESTART=1 ./scripts/start-matnorm-stack.sh`).
Предполётная проверка: `./scripts/preflight.sh`.

Add-in: `addin/matnorm-addin.zip` пересобран под `https://192.168.248.202:8123`.

## 4. Новое в админ-панели (этой итерацией)

### 4.1 «Провайдеры ИИ» (направление T-08)

- `GET/POST /api/admin/providers`, `DELETE /api/admin/providers/{id}`,
  `POST /api/admin/providers/{id}/test`.
- Пресеты: `ollama` (local), `claude`, `openai`, `deepseek`, `mimo`, `kimi`
  (external, base_url по умолчанию).
- Ключи шифруются Fernet (`SECRET_KEY` из `backend/.env`), хранятся в
  `data/admin/providers.json`, в API и UI — только маска `••••XXXX`,
  в логи не попадают (SEC-002/003).
- **Гард конфиденциальности (FR-081)**: `router.choose(confidential)` выбирает
  только `kind=local`. Внешние провайдеры дополнительно исключены из
  маршрутизации, пока `ALLOW_EXTERNAL_PROVIDERS != 1` (SEC-001, по умолчанию 0).
- «Проверить»: local → сетевая проба Ollama (`/api/tags` + наличие модели);
  external → только валидация конфигурации БЕЗ выхода в сеть; реальная проба —
  лишь при `ALLOW_EXTERNAL_PROVIDERS=1`.

### 4.2 «Подключения» (мониторинг ПК с Excel)

- Middleware учитывает обращения к `/api/*` и `/addin/*`: IP, первое/последнее
  обращение, число запросов, последний endpoint, user-agent (SEC-002 — без
  содержимого запросов).
- `GET /api/admin/clients` + снапшот `data/admin/clients.jsonl` (переживает
  рестарт). В UI не-серверные IP (ПК с Excel) подсвечены.
- В Docker за прокси реальный IP корректен благодаря `--proxy-headers`.

## 5. Docker: что исправлено и как тестировать

Исправления `docker-compose.yml` под новый код:

- порт бэкенда **8123:8000** (был 8000), TLS внутри контейнера
  (`deploy/certs` смонтированы, uvicorn с `--ssl-*` и `--proxy-headers`);
- `env_file: backend/.env` + переопределения: `INFERENCE_URL` →
  `host.docker.internal:11434` (extra_hosts `host-gateway` — работает на Linux),
  `DATABASE_URL` → sqlite на томе `/data`, `PUBLIC_BASE_URL`,
  `ALLOW_EXTERNAL_PROVIDERS=0`;
- монтирование `./addin:/addin:ro` (статика надстройки) и `./data:/data`
  (журналы админки, providers.json, exports);
- новый сервис **admin** (nginx:1.27-alpine, порт 3010) со статикой `admin/`;
- healthcheck-и у backend (https), rag и admin.

### Процедура тестового прогона в Docker (ПОСЛЕ успешного теста в Cursor env)

```bash
cd /media/data/Projects/ai-toolkit/projects/MCC

# 1. Остановить хост-стек (порты 8123/8020/3010 не должны конфликтовать!)
kill "$(cat .matnorm-backend.pid)" "$(cat .matnorm-rag.pid)" "$(cat .admin-static.pid)"

# 2. Поднять контейнеры (образы уже собраны)
docker compose -p matnorm up -d

# 3. Проверить
docker compose -p matnorm ps          # все healthy
curl -k https://192.168.248.202:8123/health
curl    http://192.168.248.202:8020/health
curl -I http://192.168.248.202:3010/

# 4. Вернуться на хост-стек
docker compose -p matnorm down
./scripts/start-matnorm-stack.sh
```

Примечание: Ollama остаётся на хосте (RTX 3060 6 ГБ) — контейнеры ходят к нему
через `host.docker.internal`. GPU-профиль `--profile gpu` — только для узла
с GPU ≥ 16 ГБ.

## 6. Куда класть тестовый каталог КД (действия пользователя)

1. Чертежи (PDF) → `data/incoming/drawings/`, 3D-модели (STEP) →
   `data/incoming/models/`. Пары связываются по совпадению имени файла
   (`АБВГ.001.002.pdf` + `АБВГ.001.002.step`); допускаются и одиночные файлы.
2. Запуск пакетной обработки:

```bash
cd /media/data/Projects/ai-toolkit/projects/MCC
./scripts/ingest-folder.sh data/incoming        # пакетный прогон каталога
./scripts/export-and-analyze.sh                 # сводный экспорт + анализ
```

3. Результаты: `data/exports/`, прогресс и журнал — в админ-панели
   (`http://192.168.248.202:3010/`, разделы «Дашборд» / «Задания» / «Экспорт»).

## 7. Чеклист действий пользователя

1. **PAT GitHub** — обновить токен (Contents: write), затем коммит/пуш
   (`scripts/gh-auth-push.sh`). До этого ничего не закоммичено — намеренно.
2. **Ключи внешних ИИ** — админка → «Провайдеры ИИ» → пресет
   (claude/openai/deepseek/mimo/kimi) → имя, модель, ключ → «Добавить» →
   «Проверить» (пока — только валидация, без сети: SEC-001).
3. **Решить про внешний egress** — внешние провайдеры заработают для
   неконфиденциальных задач только после `ALLOW_EXTERNAL_PROVIDERS=1`
   в `backend/.env` (согласовать с ИБ; см. OPEN_QUESTIONS).
4. **Тестовый каталог КД** — разложить по `data/incoming/` (см. §6).
5. **Excel ПК** — скачать `matnorm-addin.zip` из админки (раздел «Экспорт»)
   или `\\192.168.248.202` → sideload `manifest.xml`; первый запрос с этого ПК
   появится в админке → «Подключения» (подсвечен как внешний IP).
6. Ответить на открытые вопросы (`docs/OPEN_QUESTIONS.md`).

## 8. Открытые вопросы (требуют ответа пользователя)

См. `docs/OPEN_QUESTIONS.md` — обновлены: PAT, политика внешнего egress
(SEC-001), выбор DATABASE_URL (sqlite/Postgres), MinIO (да/нет),
требования аутентификации админки/API.
