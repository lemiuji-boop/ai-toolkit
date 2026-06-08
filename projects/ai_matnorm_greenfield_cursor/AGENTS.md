# AGENTS.md

## Project

AI-МАТНОРМ — ассистент технолога для анализа КД, построения КСИ и расчёта норм материалов.

## Mandatory rules

- Work in small verified increments.
- Never put all logic into one file.
- Keep deterministic calculation separate from LLM reasoning.
- Every extracted fact must store source, confidence and method.
- Never trust LLM output without schema validation.
- Never store secrets in frontend.
- Every user correction must be saved as an auditable event.
- Every calculation must be versioned.
- Every heavy task must run through a persistent queue.
- Every module must have tests or a clear test plan.

## Stack target

- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic.
- DB: PostgreSQL.
- Queue/cache: Redis.
- Object storage: MinIO/S3-compatible.
- OCR/layout: provider-based architecture.
- LLM: provider-based architecture, Ollama + external APIs.
- Frontend: Vue 3 + TypeScript + Vite.
- Desktop: Tauri.
- Excel: backend export + frontend Excel-like grid.

## Done means

- Code runs locally.
- Tests pass.
- Lint/format pass.
- Docs updated.
- No hardcoded secrets.
- No hidden mock instead of required behavior.
