# Локальные модели на 6 ГБ

Контент-движок для Telegram-канала: бенч локальных LLM через Ollama, посты с графиками, публикация по расписанию.

## Требования

- Python 3.12+
- [Ollama](https://ollama.com) на **host** (GPU, не в Docker)
- NVIDIA RTX 3060 6GB (или аналог)
- `uv` или `pip` + venv

## Установка Ollama и моделей

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
ollama pull qwen3:4b
ollama pull gemma3:4b
ollama pull phi4-mini
ollama pull qwen2.5-coder:3b
ollama pull nomic-embed-text
```

## Установка проекта

```bash
cd /path/to/tg_news_ai
uv sync --all-extras
cp .env.example .env
# отредактируйте .env: DATABASE_URL, TG_* при необходимости
```

## Миграции БД

```bash
uv run python cli.py init-db
uv run alembic upgrade head
uv run python cli.py models sync
uv run python cli.py tasks list
```

## Первый бенч

```bash
uv run python cli.py run-bench --model llama3.2:3b --suite general_ru
uv run python cli.py scores-show --experiment 1
uv run python cli.py build-post --type head_to_head --experiment 1
```

## Полный цикл

```bash
uv run python cli.py cycle --dry-run
uv run python cli.py cycle --publish   # очередь на review
uv run python cli.py bot               # scheduler
```

## Telegram

В `.env` задайте `TG_BOT_TOKEN`, `TG_TEST_CHANNEL_ID`, `TG_ADMIN_ID`.

```bash
uv run python cli.py publish --post 1
```

## Проверки качества

```bash
uv run pytest
uv run ruff check .
uv run mypy core bench content bot
uv run python scripts/gate_phase.py --phase 8
```

## Оркестрация агентами (Cursor)

См. [AGENTS.md](AGENTS.md). Команда: «Запусти llm-channel-orchestrator с фазы 0».

## Docker (опционально)

Только Postgres + API; **инференс на host Ollama**:

```bash
docker compose up -d postgres
```
