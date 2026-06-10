# Аудит безопасности и соответствия · МАТНОРМ

**Дата:** 2026-06-09  
**Контур:** on-premise Ubuntu, backend `:8123`, Cloudflare quick tunnel  
**Метод:** обзор кода, curl-пробы туннеля (локально), анализ `data/exports/` (хеши), subset re-calc (6 заданий)

> SEC-002: в этом документе **нет обозначений изделий** — только хеши `file_id`, агрегаты и счётчики.

---

## 1. Резюме

| Область | Вердикт | Критичность |
|---------|---------|-------------|
| Cloudflare quick tunnel | **Небезопасен для КД без доп. мер** | **CRITICAL** |
| API без аутентификации | Все эндпойнты публичны через туннель | **HIGH** |
| SEC-001 (egress из Python) | **Соблюдается** в коде бэкенда | OK |
| SEC-002 (логи/админка) | Частично: админ-jobs — хеши; `/api/jobs` и экспорт — полные поля | **MEDIUM** |
| CORS + tunnel regex | Любой `*.trycloudflare.com` допущен | **HIGH** |
| Соответствие ТЗ (MUST FR) | 11/11 FR прослежены в `trace.md` | OK (каркас) |
| Качество распознавания/расчёта | Vision LLM ~93%; geometry 100% stub; paired 0% | **MEDIUM** (функциональный риск) |

**Итоговый вердикт туннеля:** **UNSAFE** для конфиденциальных КД в текущей конфигурации.  
Допустим только для локальной отладки надстройки с немедленным отключением после сессии.

---

## 2. Cloudflare tunnel / gateway

### 2.1 Конфигурация

| Компонент | Значение |
|-----------|----------|
| Скрипт | `scripts/start-tunnel.sh` |
| Цель по умолчанию | `http://127.0.0.1:8123` (весь FastAPI, включая `/addin/`) |
| URL (на момент аудита) | записан в `.tunnel-url` (`*.trycloudflare.com`) |
| Автообновление | `addin/config.json` — `backendUrl` подставляется скриптом |

Туннель проксирует **единый origin**: API + статика надстройки. Ollama (`:11434`), RAG (`:8020`), админ-UI (`:3010`) **напрямую не экспонируются** — но метаданные Ollama видны через `/api/admin/status`.

### 2.2 Публичные эндпойнты (curl через tunnel, все HTTP 200)

| Путь | Назначение | Auth |
|------|------------|------|
| `GET /health` | liveness | Нет |
| `GET /version` | версия + имя VLM-модели | Нет |
| `POST /api/jobs` | загрузка чертежа/STEP, полный `JobResult` | **Нет** |
| `POST /api/normcontrol` | нормоконтроль | Нет |
| `POST /api/excel/export` | выгрузка xlsx | Нет |
| `GET /api/admin/status` | статус сервисов + список моделей Ollama | **Нет** |
| `GET /api/admin/metrics` | GPU, RAM, loadavg | Нет |
| `GET /api/admin/jobs` | журнал (job_id, input_hash) | Нет |
| `GET /api/admin/services` | детальный статус + `inference_url` | Нет |
| `GET /addin/*` | taskpane, config.json | Нет |

**Не экспонируется через tunnel:** Ollama API, RAG, порт 3010 (отдельный процесс).

### 2.3 CORS (`backend/app/core/config.py`)

- `allow_credentials=False` — cookie-сессии не используются.
- `cors_origin_regex`: `^https://[a-z0-9-]+\.trycloudflare\.com$` — **любой** субдомен trycloudflare.
- Проверка: `Origin: https://attacker-phish.trycloudflare.com` → `access-control-allow-origin` совпадает (допуск).
- `Origin: https://evil.example.com` → 400 (отклонён).

**Риск:** злоумышленник может поднять свой quick tunnel и вызывать API жертвы из браузера (CSRF-подобный сценарий при открытом туннеле).

### 2.4 SEC-001 / SEC-002

| ID | Статус | Комментарий |
|----|--------|-------------|
| SEC-001 | ✅ Python-бэкенд | `httpx` только к `INFERENCE_URL` (Ollama) и localhost-пробам в `admin_monitor.py`. Исходящих внешних API из приложения нет. Egress `cloudflared` — на уровне хоста (см. TZ §14 п.5). |
| SEC-002 | ⚠️ Частично | `job_store` / `/api/admin/jobs` — только `input_hash`. Но `POST /api/jobs` возвращает полные `designation`/`name`; `data/exports/jobs/*.json` хранит обозначения; `report_summary.json` содержит названия материалов в агрегатах. |
| SEC-003 | ✅ | Секреты через `.env`; `.env.example` без значений. |
| SEC-004 | ✅ | Версии в `pyproject.toml`. |

### 2.5 Утечки данных

1. **Загрузка КД без auth** — любой, кто знает URL туннеля, может отправить чертёж и получить распознанные поля.
2. **Admin `/status`** — раскрывает имена моделей Ollama, latency, число заданий.
3. **Admin `/metrics`** — GPU, память хоста (разведка инфраструктуры).
4. **`addin/config.json`** — публичный URL бэкенда.
5. **Журнал экспорта** — JSON-файлы на диске с полными полями (не через tunnel, но на хосте).

### 2.6 Рекомендации (по приоритету)

| Severity | Рекомендация |
|----------|--------------|
| **CRITICAL** | Не держать quick tunnel постоянно включённым при реальных КД. Останавливать `cloudflared` после отладки. |
| **CRITICAL** | Перед продом: API token / mTLS / IP allowlist на reverse-proxy; минимум — Bearer для `/api/jobs` и `/api/admin/*`. |
| **HIGH** | Убрать или ограничить `cors_origin_regex` до конкретного named tunnel hostname (не wildcard `*.trycloudflare.com`). |
| **HIGH** | Не отдавать список моделей Ollama через публичный `/api/admin/status`; вынести админку за VPN. |
| **MEDIUM** | Rate limiting на `POST /api/jobs` (размер файла, RPS). |
| **MEDIUM** | Агрегаты в `report_summary` — хешировать материалы или коды, не plaintext. |
| **LOW** | Named tunnel + Cloudflare Access вместо quick tunnel. |

---

## 3. Соответствие ТЗ

### 3.1 MUST FR (§6)

| FR | Статус | Пробел |
|----|--------|--------|
| FR-001 | ✅ | — |
| FR-002 | ✅ | debug-зоны только при `?debug=true` |
| FR-003 | ✅ | — |
| FR-004 | ✅ | stub при ошибке VLM — риск «выдуманных» полей в stub-ветке |
| FR-007 | ✅ | — |
| FR-010 | ⚠️ | cadquery не задействован на реальных STEP (100% `source=stub`) |
| FR-011 | ✅ | детерминированный `calc.py` |
| FR-012 | ⚠️ | paired не прогонялся (0 пар в экспорте) |
| FR-013 | ✅ | — |
| FR-014 | ✅ | тесты на stub-сборке; на реальных КД деревьев нет |
| FR-015 | ✅ | SHOULD выполнен |

**Оценка MUST FR:** **~91%** по коду/тестам; **~60%** по операционной валидации на реальных КД (geometry stub, нет paired).

### 3.2 Дополнительно к ТЗ (в `trace.md`, вне §6)

- FR-016 (режимы job) — реализован
- ADM-001 — админ API без auth (открытый вопрос TZ §14 п.4)
- EXP-001, ADD-001 — экспорт и tunnel

### 3.3 Definition of Done (§15)

| Критерий | Статус |
|----------|--------|
| MUST FR + тесты | ✅ 37 pytest |
| `ruff` / `mypy` | ✅ |
| `/api/jobs` на реальной паре PDF+STEP | ❌ paired=0 в полном экспорте |
| Заглушки при недоступном inference | ✅ |
| Контейнер + `/health` | не проверялось в этом аудите |

### 3.4 Открытые вопросы (§14)

| # | Тема | Статус аудита |
|---|------|---------------|
| 1 | TLS / mixed content | Актуален: tunnel даёт HTTPS |
| 2 | Допустимость Vercel | Не оценивался |
| 3 | Кириллица в OCR/VLM | Работает на выборке (LLM 28/30) |
| 4 | Auth админ-панели | **Не решён** — API открыт через tunnel |
| 5 | Cloudflare quick tunnel | **Подтверждён риск** — публичный URL без auth |

---

## 4. Распознавание и логика конвейера

### 4.1 Pipeline

```
POST /api/jobs
  → ocr.preprocess (PDF→PNG, зоны)     [FR-002]
  → vision.extract (Ollama VLM)        [FR-003/004]
  → geometry.geometry (cadquery|stub)  [FR-010]
  → verify.verify (чертёж↔3D)          [FR-012]
  → calc.build_rows + normcontrol      [FR-011/013/014/015]
```

### 4.2 Статистика полного экспорта (30 заданий, `data/exports/`)

| Метрика | Значение |
|---------|----------|
| drawing_only | 29 |
| model_only | 1 |
| paired | **0** |
| vision `llm` / `stub` | 28 / 2 |
| geometry `cad` / `stub` | 0 / **30** |
| material отсутствует | 14 (47%) |
| mass_kg = null | 9 (30%) |
| kim = null | 9 (30%) |
| trees_built | 0 |

### 4.3 Паттерны точности

1. **Марка материала** — часто `null` на сборочных листах (СБ) и спецификациях (СП); VLM читает основную надпись детали лучше, чем таблицу спецификации.
2. **Сборка vs деталь** — листы с суффиксом СБ/СП дают 1 строку ведомости вместо дерева; `is_assembly=false` везде (geometry stub).
3. **Stub vision** — при таймауте VLM (`INFERENCE_TIMEOUT=120`) откат к демо-полям `АБВГ.001.001` (file_id `cfaf189ce872`).
4. **Масса без материала** — расчёт идёт по `mass_kg` с чертежа, но флаг «нет марки»; ~5.7 т из ~5.8 т `norm_program_kg` — строки с пустым material (агрегат по пустой строке).
5. **Сверка** — в режиме `drawing_only` только INFO-флаг; реальная FR-012 не задействована.

### 4.4 Сравнение структуры с эталонным XLSX

| | Эталон (`ref_8417e4e56dc9`, `ref_f6ada4716991`) | API / экспорт |
|--|--|--|
| Листов | 2–3 (титульник, ТСИ, расчёт) | 1 виртуальная ведомость |
| Строк ТСИ | 804 / 1159 | 1 row/job |
| Колонок | ~103 (заголовок строка 2) | 12 (`NormRow`) |
| Поля норм | кол. ~66+ в ТСИ | `md_kg`, `mz_kg`, `kim`, `norm_program_kg` |

Автоматического diff чисел с XLSX **нет** (разная гранулярность: программа целиком vs одна деталь на PDF).

---

## 5. Пересчёт (subset, 6 заданий)

Прогон: `/tmp/mcc-audit-subset` (5 PDF + 1 STP), `VLM_MODEL=qwen3-vl:8b-instruct`, 96 с.

| file_id | mode | extract | material | norm_program_kg | Примечание |
|---------|------|---------|----------|-----------------|------------|
| `2712a0d3d664` | drawing_only | llm | ❌ | 5.71 | СБ-лист: масса есть, материала нет |
| `685e50670547` | drawing_only | llm | ❌ | null | СБ-установка: нет массы/материала |
| `91f66e2c5b5b` | drawing_only | llm | ✅ | 0.0015 | Деталь: полный расчёт |
| `addf0746b836` | drawing_only | llm | ✅ | 0.0059 | Деталь: полный расчёт |
| `e5db4ba5ae16` | drawing_only | llm | ✅ | 0.156 | Деталь: полный расчёт |
| `f661d06700be` | model_only | stub | ❌ | null | STEP без cadquery → stub |

**Качество расчёта vs Excel (качественно):** формулы `calc.py` консистентны (КИМ ≈ 0.74 при наличии Мд); расхождение с эталоном обусловлено **входом** (нет материала, нет paired, одна строка на файл), а не арифметикой ядра.

---

## 6. Локальные модели (Ollama)

Доступно 9 моделей; vision-тест на одном PDF (hash `4b3c4e3cb9a7`, 284 КБ):

| Модель | Latency, s | source | confidence_avg | Поля |
|--------|------------|--------|----------------|------|
| `qwen3-vl:8b` | 121.3 | stub (timeout) | 0.5 | 4 (заглушка) |
| `qwen3-vl:8b-instruct` | 38.7 | llm | 0.91 | 3 (+ dims) |
| `qwen2.5vl:3b` | 1.1 | stub (не установлена) | 0.5 | 4 (заглушка) |

**Рекомендация:** `VLM_MODEL=qwen3-vl:8b-instruct`, `INFERENCE_TIMEOUT≥180` для 8B.

---

## 7. Тесты

```
ruff check .  → OK
mypy app      → OK
pytest -q     → 37 passed (+1 audit test)
```

Добавлен `test_admin_endpoints_no_sensitive_leaks` — проверка отсутствия filename/designation/path в `/api/admin/jobs`.

---

## 8. Созданные/обновлённые файлы

| Файл | Действие |
|------|----------|
| `docs/security-audit.md` | создан (этот документ) |
| `backend/.env.example` | дополнен документацией моделей |
| `backend/tests/test_audit_security.py` | создан |
