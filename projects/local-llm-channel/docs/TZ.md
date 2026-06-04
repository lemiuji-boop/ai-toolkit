# ТЗ для Cursor: Контент-движок Telegram-канала «Локальные модели на 6 ГБ»

> **Назначение файла.** Это полная инструкция для AI-агента Cursor: цель, архитектура, пофазный план реализации, схемы данных, план экспериментов, список моделей и редакционный план. Технические спецификации, код, имена файлов и команды — на английском. Стратегия и тексты для канала — на русском.
>
> **Дата составления:** 2026-06-01. Цифры по скорости/VRAM ниже — ориентировочные оценки; реальные значения система измеряет сама (в этом весь смысл бенч-харнесса).

---

## 0. TL;DR для агента

Построй монорепозиторий на Python 3.12, который:

1. **Гоняет локальные LLM** через Ollama (host) по стандартизированному набору задач и собирает метрики (tok/s, TTFT, peak VRAM, quality score).
2. **Хранит результаты** в БД (SQLite по умолчанию, опционально PostgreSQL).
3. **Генерирует посты** для Telegram из результатов: текст + таблицы + графики (PNG).
4. **Публикует** в Telegram-канал по расписанию с воркфлоу draft → review → publish.
5. **Оркестрируется** одной CLI-командой: `pick model → run bench → build post → schedule`.

Реализуй **строго по фазам** (раздел 6). Каждая фаза заканчивается рабочим, проверяемым артефактом. Не делай заглушек и моков в продакшен-коде — только production-ready реализации.

---

## 1. Цель проекта и редакционная идея

**Цель:** автоматизировать ведение Telegram-канала об обзорах, запуске и сравнении локальных LLM на потребительском железе.

**Ниша (ключевое отличие):** честные эксперименты на **ноутбуке с RTX 3060 (6 ГБ VRAM)** — то железо, что есть у большинства читателей, а не у владельцев 24-гигабайтных карт. Реальные tok/s, реальный peak VRAM, реальное «влезло / не влезло / влезло, но больно».

**Тон канала:** прикладной, без хайпа, с воспроизводимыми командами (`ollama pull ...`) и цифрами.

**Язык канала:** русский. Код и спецификации — английский.

---

## 2. Аппаратные и платформенные ограничения (вшить в конфиг)

| Параметр | Значение | Следствие для архитектуры |
|---|---|---|
| GPU | NVIDIA RTX 3060 Laptop, **6 ГБ VRAM** | Бюджет весов ≤ ~5.0 ГБ, остальное — KV-cache + ОС |
| RAM | 16–32 ГБ | Возможен CPU-offload для 7–12B (медленно, но публикабельно) |
| OS | Windows 11 + WSL2 **или** Linux | Ollama — на host; Docker GPU-passthrough на ноуте ненадёжен |
| Inference backend | Ollama (primary), llama.cpp (advanced) | Бенч ходит в `http://localhost:11434` |

**Правило бюджета VRAM (вшить как формула в `bench/vram.py`):**
`weights_GB ≈ params_B × 0.6 (Q4_K_M)`; добавь **+10–20 %** на KV-cache при длинном контексте. На 6 ГБ оставляй **1.0–1.5 ГБ** запаса под ОС/драйвер.

**Архитектурный вывод:** Ollama запускается **нативно на host** (имеет доступ к GPU). Остальное (БД, бот, генератор, API) — нативный venv по умолчанию; Docker Compose опционален и поднимает только stateless-сервисы + Postgres. **Не контейнеризируй сам инференс.**

---

## 3. Технологический стек

**Backend / общий**
- Python 3.12, `uv` или `pip` + venv
- `pydantic` v2 (config, schemas), `pydantic-settings`
- `SQLAlchemy` 2.x async + `alembic` (миграции)
- БД: `aiosqlite` (default) / `asyncpg` (Postgres, опц.)
- `httpx` (Ollama API, Telegram Bot API)
- `ollama` (официальный python-клиент) — для удобства, fallback на httpx

**Бенч / метрики**
- `pynvml` (peak VRAM через NVML) — primary; fallback: парсинг `nvidia-smi`
- `psutil` (RAM/CPU)
- Скоринг: rule-based + LLM-as-judge (локальный 8B или Anthropic API — переключаемо)

**Контент**
- `matplotlib` (headless, `Agg`) → PNG-графики
- `Jinja2` (шаблоны постов)
- `Pillow` (склейка/ресайз изображений, при необходимости)

**Telegram**
- `aiogram` 3.x (бот, channel publishing, review-флоу)
- `APScheduler` (расписание публикаций)

**Оркестрация / DX**
- `typer` (CLI)
- `rich` (логи/таблицы в консоли)
- `ruff` + `mypy` (линт/типы), `pytest` (тесты)
- Опц.: `FastAPI` + `uvicorn` (admin API), `docker-compose`

---

## 4. Архитектура системы

```
                       ┌─────────────────────────────────────────┐
                       │              CLI (typer)                 │
                       │   run-bench · build-post · publish · cycle│
                       └───────────────┬──────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌───────────────┐            ┌──────────────────┐           ┌──────────────────┐
│   bench/      │            │    content/      │           │      bot/        │
│  runner       │            │   generator      │           │   publisher      │
│  ├ tasks/     │            │   ├ templates/   │           │   ├ scheduler    │
│  ├ scorers/   │   results  │   ├ charts.py    │   posts   │   ├ editorial    │
│  └ vram.py    │ ─────────▶ │   └ render.py    │ ────────▶ │   └ review flow  │
└───────┬───────┘            └─────────┬────────┘           └────────┬─────────┘
        │                              │                             │
        │     ┌────────────────────────┴─────────────────────────┐   │
        └────▶│                    core/ (shared)                 │◀──┘
              │   db.py · models.py · schemas.py · config.py      │
              └───────────────────────┬───────────────────────────┘
                                       ▼
                          ┌──────────────────────┐         ┌────────────────────┐
                          │  DB (SQLite/Postgres)│         │  Ollama @ host:11434│
                          │  experiments·runs·   │◀───────▶│  (GPU inference)    │
                          │  scores·posts        │  HTTP   └────────────────────┘
                          └──────────────────────┘
```

**Потоки данных:**
1. `bench.runner` берёт `Model × TaskSuite`, гоняет через Ollama, пишет `Run` + `Metric` + `Score` в БД и сырые выводы в `bench/results/`.
2. `content.generator` читает результаты, строит графики (`charts.py`) и рендерит пост из Jinja-шаблона → `Post` (draft) + media-файлы.
3. `bot.publisher` берёт `Post` со статусом `approved`, публикует в канал по расписанию.

---

## 5. Структура репозитория

```
llm-channel/
├── pyproject.toml
├── .env.example
├── README.md                  # RU: setup + запуск (генерится в Фазе 8)
├── docker-compose.yml         # опц.: postgres + bot + api
├── alembic.ini
├── migrations/
│
├── core/
│   ├── __init__.py
│   ├── config.py              # Settings (pydantic-settings)
│   ├── db.py                  # async engine, session factory
│   ├── models.py              # SQLAlchemy ORM
│   └── schemas.py             # Pydantic DTO
│
├── bench/
│   ├── __init__.py
│   ├── runner.py              # оркестрация прогона
│   ├── ollama_client.py       # обёртка над Ollama API (+ метрики из ответа)
│   ├── vram.py                # NVML peak-VRAM сэмплер (поток)
│   ├── registry.py            # загрузка models.yaml → ORM
│   ├── models.yaml            # КАТАЛОГ МОДЕЛЕЙ (раздел 9)
│   ├── tasks/                 # наборы задач (раздел 8)
│   │   ├── __init__.py
│   │   ├── base.py            # Task, TaskSuite, TaskResult
│   │   ├── general_ru.yaml
│   │   ├── coding.yaml
│   │   ├── reasoning.yaml
│   │   ├── summarization_ru.yaml
│   │   ├── rag.yaml
│   │   ├── function_calling.yaml
│   │   ├── long_context.yaml
│   │   └── creative_ru.yaml
│   ├── scorers/
│   │   ├── __init__.py
│   │   ├── rule_based.py      # exact/regex/json-valid/code-exec
│   │   ├── judge.py           # LLM-as-judge (local | anthropic)
│   │   └── speed.py           # tok/s, TTFT агрегаты
│   └── results/               # raw .jsonl выводы (gitignored)
│
├── content/
│   ├── __init__.py
│   ├── generator.py           # results → Post (draft)
│   ├── charts.py              # matplotlib → PNG
│   ├── render.py              # Jinja → markdown/HTML текст
│   └── templates/             # RU шаблоны постов (раздел 10)
│       ├── model_review.md.j2
│       ├── head_to_head.md.j2
│       ├── fits_6gb.md.j2
│       ├── benchmark_roundup.md.j2
│       ├── howto.md.j2
│       └── news.md.j2
│
├── bot/
│   ├── __init__.py
│   ├── publisher.py           # aiogram: публикация в канал
│   ├── scheduler.py           # APScheduler джобы
│   ├── editorial.py           # календарь, выбор следующей темы
│   └── review.py              # draft → approve в личке админу
│
├── api/                       # опц. admin
│   ├── __init__.py
│   └── main.py                # FastAPI: /experiments /posts /calendar
│
├── cli.py                     # typer entrypoint
└── tests/
    ├── test_vram.py
    ├── test_scorers.py
    ├── test_generator.py
    └── test_runner_smoke.py
```

---

## 6. Пофазный план реализации (Cursor выполняет по порядку)

> После каждой фазы — рабочий артефакт и критерий приёмки (DoD). Не переходи к следующей фазе, пока DoD текущей не выполнен.

### Фаза 0 — Каркас
- `pyproject.toml`, `.env.example`, `ruff`/`mypy`/`pytest` конфиги, `core/config.py`.
- **DoD:** `python cli.py --help` запускается; `ruff check` чистый.

### Фаза 1 — Ядро данных
- `core/db.py` (async engine, `DATABASE_URL` из env, default `sqlite+aiosqlite:///./data/app.db`).
- `core/models.py` (раздел 7), `core/schemas.py`, alembic init + первая миграция.
- **DoD:** `alembic upgrade head` создаёт схему; smoke-тест CRUD проходит.

### Фаза 2 — Реестр моделей и задач
- `bench/registry.py` парсит `bench/models.yaml` → таблицу `models`.
- `bench/tasks/base.py` + загрузчик YAML-наборов задач.
- **DoD:** `python cli.py models list` и `python cli.py tasks list` печатают каталог из БД.

### Фаза 3 — Бенч-харнесс (ядро ценности)
- `bench/ollama_client.py`: chat/generate, извлечение из ответа Ollama `eval_count`, `eval_duration`, `prompt_eval_*`, `total_duration` → tok/s, TTFT.
- `bench/vram.py`: фоновый поток NVML, сэмплит `usedGpuMemory` каждые 100 мс → peak.
- `bench/runner.py`: для `Model × Task` — warm-up прогон + `N_REPEATS` замеров, фиксированные `temperature/seed/num_ctx/num_predict`; запись `Run`/`Metric`.
- **DoD:** `python cli.py run-bench --model llama3.2:3b --suite general_ru` создаёт записи Run с tok/s и peak VRAM; raw-вывод в `bench/results/*.jsonl`.

### Фаза 4 — Скоринг качества
- `scorers/rule_based.py`: точное совпадение, regex, JSON-валидность, выполнение кода в sandbox (`subprocess` + timeout, без сети).
- `scorers/judge.py`: LLM-as-judge, рубрика 0–5, режимы `local` (8B-модель) / `anthropic` (Claude). Для RU-задач — судья оценивает по-русски.
- **DoD:** у каждого `Run` появляется `Score`; `python cli.py scores show --experiment <id>` даёт сводную таблицу.

### Фаза 5 — Графики и генерация постов
- `content/charts.py`: бар-чарты (tok/s по моделям, peak VRAM, quality по категориям), линия (tok/s vs context length). Тёмная тема, единый брендинг, PNG 1280×720.
- `content/render.py` + `content/generator.py`: results → `Post(draft)` по шаблону.
- **DoD:** `python cli.py build-post --type head_to_head --experiment <id>` создаёт `Post` + PNG; текст валиден для Telegram (≤ 4096 симв. на сообщение / ≤ 1024 на caption).

### Фаза 6 — Telegram-публикация
- `bot/publisher.py` (aiogram 3): постинг текста + media-group в канал по `CHANNEL_ID`.
- `bot/review.py`: draft уходит админу в ЛС с инлайн-кнопками Approve/Reject/Edit.
- `bot/scheduler.py` (APScheduler): публикация `approved`-постов по слотам календаря.
- **DoD:** approved-пост публикуется в тестовый канал; статус в БД → `published` с `tg_message_id`.

### Фаза 7 — Оркестрация и редакционный календарь
- `bot/editorial.py`: выбор следующей темы по календарю (раздел 10), защита от повторов.
- `cli.py cycle`: end-to-end `pick → bench → score → build → queue`.
- **DoD:** `python cli.py cycle --dry-run` проходит весь конвейер без публикации; `--publish` ставит в очередь.

### Фаза 8 — Документация и упаковка
- RU `README.md`: установка Ollama, pull базовых моделей, миграции, .env, запуск бота, первый цикл.
- Опц. `docker-compose.yml` (postgres + bot + api), `Makefile`/`justfile`.
- **DoD:** по README с нуля поднимается рабочий цикл; `pytest` зелёный.

---

## 7. Модель данных (ORM, раздел `core/models.py`)

```python
# Псевдо-схема — реализуй на SQLAlchemy 2.x (Mapped[], mapped_column)

Model:
    id: int (pk)
    name: str                 # человекочитаемое: "Qwen3 4B"
    ollama_tag: str (unique)  # "qwen3:4b-q4_K_M"
    params_b: float           # 4.0
    quant: str                # "Q4_K_M"
    family: str               # "qwen3" | "llama" | "gemma" | "phi" | ...
    est_vram_gb: float
    fits_6gb: enum(yes|tight|offload|no)
    context_max: int
    modality: enum(text|vision|code)
    license: str
    notes: str | None

TaskSuite:
    id, name, category(enum), language(enum ru|en|mixed), description

Task:
    id, suite_id(fk), key, prompt, system_prompt|None,
    expected|None, scorer(enum exact|regex|json|code|judge),
    scorer_config: json, max_tokens: int, weight: float

Experiment:
    id, title, kind(enum), created_at, config: json   # что и зачем гоняем

Run:
    id, experiment_id(fk), model_id(fk), task_id(fk),
    started_at, finished_at, seed, temperature, num_ctx, num_predict,
    output_text, output_path,           # ссылка на jsonl
    status(enum ok|error|oom), error|None

Metric:
    id, run_id(fk),
    tok_per_sec: float, ttft_ms: float,
    prompt_tokens: int, eval_tokens: int,
    peak_vram_mb: int, peak_ram_mb: int, total_ms: float

Score:
    id, run_id(fk), scorer: str, value: float (0..1 norm),
    raw: json,   # рубрика судьи / результат тестов
    rationale: str | None

Post:
    id, experiment_id(fk)|None, kind(enum), title,
    body_md: text, media_paths: json,
    status(enum draft|review|approved|scheduled|published|rejected),
    scheduled_at|None, published_at|None, tg_message_id|None

CalendarSlot:
    id, weekday(int), time_local(str), rubric(enum), active(bool)
```

`Experiment.kind` / `Post.kind` (общий enum рубрик):
`model_review | head_to_head | fits_6gb | benchmark_roundup | howto | news`.

---

## 8. Детальный план экспериментов

### 8.1 Методология (вшить в `runner.py`, документировать в постах)
- **Фиксированные параметры по умолчанию:** `temperature=0.0` (для детерминизма скоринга; для creative — 0.7), `seed=42`, `num_predict` задаётся per-task, `num_ctx` — отдельный профиль (см. 8.3 long-context).
- **Прогрев:** 1 warm-up прогон (не учитывается) для загрузки весов в VRAM.
- **Повторы:** `N_REPEATS=3`, в метрики идёт медиана tok/s и **максимум** peak VRAM.
- **Изоляция:** перед каждой моделью — выгрузка предыдущей (`ollama stop` / keep_alive=0), пауза 3 с, фиксация «холодного» состояния VRAM.
- **Запись окружения:** Ollama version, драйвер, фактический quant, реально загруженные слои на GPU vs CPU (из логов Ollama).
- **Метрики:** `tok/s` (eval rate), `TTFT` (prompt_eval_duration), `peak VRAM`, `peak RAM`, `quality (0..1)`.

### 8.2 Наборы задач (по 8–15 заданий в каждом, RU-приоритет)

| Категория | Что проверяем | Скорер | Примеры заданий |
|---|---|---|---|
| `general_ru` | Следование инструкции, RU-грамотность | judge | переписать абзац в деловом стиле; извлечь поля в список |
| `coding` | Генерация кода | code-exec + judge | мини-HumanEval (8–10 функций) + 2–3 реальных сниппета |
| `reasoning` | Логика / математика | exact/regex + judge | подвыборка GSM8K, логические задачи, цепочка рассуждений |
| `summarization_ru` | Сжатие длинного RU-текста | judge | статья 2–3к слов → 5 пунктов; сохранение фактов |
| `rag` | QA по предоставленному контексту | exact + judge | ответ строго из контекста; отказ при отсутствии ответа |
| `function_calling` | Корректность tool-call JSON | json-valid + schema | вызвать `get_weather(city,date)`; не выдумывать аргументы |
| `long_context` | Needle-in-haystack | exact | факт спрятан на 8k/16k/32k токенах |
| `creative_ru` | Стиль, копирайтинг | judge (temp 0.7) | пост для Telegram в заданном тоне |

### 8.3 Спец-эксперименты (отдельные `Experiment.kind`)
1. **Профиль скорости vs контекст:** один промпт при `num_ctx ∈ {2k, 4k, 8k, 16k, 32k}` → график tok/s и peak VRAM от длины. Показывает, где модель «вываливается» из 6 ГБ.
2. **Quant-дуэль:** одна модель в `Q4_K_M` vs `Q5_K_M` vs `Q8_0` → качество/скорость/VRAM (где влезает).
3. **Дуэль моделей (head-to-head):** 2–3 модели одного класса на всех наборах → радар качества + бар tok/s + бар VRAM.
4. **«Влезет ли в 6 ГБ?»:** систематический прогон модели с фиксацией `fits_6gb` (yes/tight/offload/no) и фактической доли слоёв на GPU.

### 8.4 Маппинг эксперимент → пост
- профиль скорости → `model_review`
- quant-дуэль → `benchmark_roundup`
- head-to-head → `head_to_head`
- влезаемость → `fits_6gb`

---

## 9. Список моделей под RTX 3060 6 ГБ (`bench/models.yaml`)

> Тиры по влезаемости в **6 ГБ**. Конкретные tok/s/VRAM — ориентиры; харнесс измеряет фактические значения. Перед `pull` агент проверяет актуальный тег на `ollama.com/library` (теги меняются).

### Tier S — «комфортно, целиком на GPU» (основа канала)
| Модель | Ollama tag (проверить) | Параметры | Quant | ~VRAM | Назначение |
|---|---|---|---|---|---|
| Llama 3.2 3B | `llama3.2:3b` | 3B | Q4_K_M | ~2.5–3 ГБ | базовый general/RU, эталон скорости |
| Qwen3 4B | `qwen3:4b` | 4B | Q4_K_M | ~3–3.5 ГБ | сильный general + код, tool-calling |
| Gemma 3 4B | `gemma3:4b` | 4B | Q4_K_M | ~3.5 ГБ | мультимодальная (vision), RU-чат |
| Phi-4-mini | `phi4-mini` | 3.8B | Q4_K_M | ~3 ГБ | reasoning/STEM на устройстве |
| Gemma 4 e4b | `gemma4:e4b` | MoE (3B акт.) | Q4 | ~6–8 ГБ* | tool-calling + vision (тестировать впритык) |
| Qwen2.5-Coder 3B | `qwen2.5-coder:3b` | 3B | Q4_K_M | ~2.5 ГБ | лёгкий кодер для слабого железа |
| SmolLM2 1.7B | `smollm2:1.7b` | 1.7B | Q4_K_M | ~1.5 ГБ | максимальная скорость, прототипы |

\* Gemma 4 e4b — на границе 6 ГБ; пометить как `tight`, замерить реально.

### Tier A — «впритык: Q4, урезанный контекст, частичный оффлоад»
| Модель | Ollama tag | Параметры | Quant | ~VRAM | Заметка |
|---|---|---|---|---|---|
| Qwen3 8B | `qwen3:8b` | 8B | Q4_K_M | ~5.2 ГБ | малый контекст; ~15–22 ток/с при оффлоаде |
| Llama 3.1 8B | `llama3.1:8b` | 8B | Q4_K_M | ~5 ГБ | классический general-эталон |
| Mistral 7B | `mistral` | 7B | Q4_K_M | ~4.5 ГБ | самый быстрый в классе 7B |
| Qwen2.5-Coder 7B | `qwen2.5-coder:7b` | 7B | Q4_K_M | ~4.7 ГБ | лучший доступный кодер на 6 ГБ |
| DeepSeek-R1 distill 7/8B | `deepseek-r1:7b` | 7–8B | Q4_K_M | ~5 ГБ | reasoning с chain-of-thought |
| Mistral Nemo 12B | `mistral-nemo` | 12B | Q4_K_M | ~7.5 ГБ | сильный оффлоад на CPU, медленно — но контентно |

### Tier B — «для контраста: что даёт переход на 12 ГБ»
| Модель | Ollama tag | Параметры | ~VRAM | Зачем в канале |
|---|---|---|---|---|
| Llama 4 Scout | `llama4:scout` | MoE 17B акт./109B | ~10 ГБ | «вот что вы получаете на десктопной 3060 12 ГБ» |
| Gemma 3/4 12B | `gemma3:12b` / `gemma4:e12b` | 12B | ~9–16 ГБ | апгрейд-нарратив |

### Vision и RAG-компоненты
- **Vision:** `gemma3:4b` (влезает), `llama3.2-vision:11b` (оффлоад, для демо).
- **Embeddings (для RAG-задач):** `nomic-embed-text`, `bge-m3`.

**Базовый стартовый набор для `ollama pull` (Фаза 8 README):**
`llama3.2:3b`, `qwen3:4b`, `gemma3:4b`, `phi4-mini`, `qwen2.5-coder:3b`, `nomic-embed-text`.

---

## 10. Редакционный план и шаблоны постов

### 10.1 Рубрики (`Post.kind`)
1. **`model_review`** — «Разбор одной модели»: что это, влезает ли, tok/s, на чём хороша/слабка, вердикт + `ollama pull`.
2. **`head_to_head`** — «Дуэль»: 2–3 модели одного класса, радар качества + бары скорости/VRAM, кого выбрать.
3. **`fits_6gb`** — «Влезет ли в 6 ГБ?»: короткий вердикт yes/tight/offload/no + цифры.
4. **`benchmark_roundup`** — «Бенч-таблица недели»: сводная таблица по категориям.
5. **`howto`** — «Гайд»: установка, quant, num_ctx, оффлоад, ускорение на 6 ГБ.
6. **`news`** — «Новости локальных моделей»: новый релиз → быстрый тест-драйв на 6 ГБ.

### 10.2 Календарь (default `CalendarSlot`, 3–4 поста/нед.)
| День | Время (local) | Рубрика |
|---|---|---|
| Пн | 12:00 | benchmark_roundup |
| Ср | 19:00 | head_to_head **или** model_review |
| Пт | 19:00 | fits_6gb **или** howto |
| Сб | 12:00 | news (если есть инфоповод) |

### 10.3 Анатомия поста (вшить в Jinja-шаблоны)
1. **Хук** (1 строка): «Qwen3 4B на 6 ГБ — 34 ток/с. Стоит ли оно того?»
2. **Сетап**: железо (RTX 3060 6 ГБ), quant, num_ctx — для воспроизводимости.
3. **Метод**: какие задачи, сколько повторов (1 строка + ссылка на методологию).
4. **Результаты**: таблица + 1–2 PNG-графика.
5. **Вердикт**: 2–3 предложения, для кого.
6. **Команда**: `ollama pull <tag>` в блоке кода.
7. **CTA**: вопрос аудитории / опрос.

> Лимиты Telegram (вшить в `render.py`): текст сообщения ≤ 4096 символов, подпись к медиа ≤ 1024. Длинный разбор — текст отдельным сообщением + media-group следом, либо разбивка.

---

## 11. Конфигурация (`.env.example`)

```dotenv
# DB
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/llmchannel

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
N_REPEATS=3
DEFAULT_SEED=42

# Hardware budget
GPU_VRAM_GB=6
VRAM_SAFETY_GB=1.2

# Scoring judge: local | anthropic
JUDGE_MODE=local
JUDGE_LOCAL_MODEL=qwen3:8b
ANTHROPIC_API_KEY=            # нужен только при JUDGE_MODE=anthropic

# Telegram
TG_BOT_TOKEN=
TG_CHANNEL_ID=                # @channel или -100...
TG_ADMIN_ID=                  # для review-флоу
TG_TEST_CHANNEL_ID=           # для прогона публикации

# Branding
BRAND_NAME=Локальные модели на 6 ГБ
CHART_THEME=dark
```

---

## 12. CLI-команды (`cli.py`, typer)

```bash
python cli.py models list|add|pull          # реестр моделей
python cli.py tasks list                     # наборы задач
python cli.py run-bench --model <tag> --suite <name> [--ctx 4096]
python cli.py run-experiment --kind head_to_head --models a,b,c --suites all
python cli.py scores show --experiment <id>
python cli.py build-post --type <kind> --experiment <id>
python cli.py publish --post <id>            # ручная публикация
python cli.py cycle [--dry-run | --publish]  # полный конвейер
python cli.py bot run                        # запустить бота + scheduler
```

---

## 13. Конвенции для агента (`.cursorrules`)

- Только **async** в I/O-слое (БД, Ollama, Telegram). Никаких блокирующих вызовов в event loop — `pynvml`/`subprocess` оборачивать в `asyncio.to_thread`.
- **Никаких заглушек** в продакшен-коде. Если не хватает данных — fail loud с понятной ошибкой.
- Все внешние параметры — через `core/config.Settings`, не хардкодить.
- Типизация: `mypy --strict` на `core/`, `bench/`, `content/`.
- Каждая фаза = отдельный коммит со своим DoD и тестом.
- Тексты постов и README — на русском; код, докстринги, имена — на английском.
- Перед `ollama pull` — проверять актуальный тег (теги в каталоге меняются).
- Sandbox для code-exec: `subprocess` с `timeout`, без сети, отдельная временная директория.

---

## 14. Критерии готовности всего проекта (Definition of Done)

1. `python cli.py cycle --publish` выполняет полный путь: выбор темы → бенч → скоринг → пост с графиками → очередь публикации.
2. Реальный пост с таблицей и ≥1 графиком опубликован в тестовый канал.
3. БД содержит воспроизводимые `Run`/`Metric`/`Score` с реальными tok/s и peak VRAM на RTX 3060 6 ГБ.
4. `pytest` зелёный; `ruff`/`mypy` чистые.
5. По RU-`README.md` проект поднимается с нуля.
