# START HERE для Cursor

## Цель

Разработать AI-МАТНОРМ с нуля как полноценный стек:

```text
FastAPI backend
PostgreSQL
Redis queue
MinIO file storage
OCR/Layout pipeline
LLM router: Ollama + API providers
Vue/Vite frontend
Tauri Windows app
Admin panel
RBAC/security/audit
Excel-like editor + export templates
```

## Как работать

1. Не пытайся за один проход написать всю систему.
2. Сначала создай устойчивый каркас.
3. После каждого этапа запускай тесты.
4. Не удаляй документацию.
5. Все TODO помечай явно.
6. Не храни секреты в коде.
7. Все long-running задачи выноси в worker.

## Первый запрос в Cursor

**Актуальное ТЗ:** `docs/TZ.md` (16 разделов, FR/NFR/SEC).

Открой `prompts/CURSOR_MASTER_PROMPT.md` или индекс `prompts/MILESTONE_INDEX.md`.

Проверка: `./scripts/verify.sh`
