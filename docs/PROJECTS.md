# Project Guide

## Task Feasibility

A guarded multi-agent pipeline for assessing technical work before implementation. It classifies complexity, checks unsafe requests, estimates feasibility and token cost, and produces a Markdown implementation brief. Heuristic fallbacks keep tests independent of live LLM providers.

- `backend/app/guardrails/` - safety shield and filtering
- `backend/app/agents/` - routing and analysis graph
- `backend/app/services/` - estimation and document generation
- `frontend/src/` - browser UI

## Local LLM Channel

Discovers Ollama models, runs configurable benchmark suites, captures VRAM and throughput, persists experiments, builds charts and posts, and routes content through review before Telegram publication.

- `bench/` - model registry, runner, and telemetry
- `content/` - chart and post generation
- `bot/` - review, scheduling, and publication
- `tests/` - smoke and unit coverage

## Neuropoligon

An interactive AI-learning application for Android, desktop, and web. Kotlin Multiplatform keeps domain logic and Compose UI in a shared module while thin platform shells provide native entry points.

- `shared/src/commonMain/` - domain, data, UI, and course resources
- `shared/src/commonTest/` - shared tests
- `androidApp/`, `desktopApp/`, `webApp/` - platform entry points

## Impossible Travel

A multi-stage content studio for stories about impossible places. A Next.js dashboard starts and reviews episodes, FastAPI owns the workflow, Celery runs background tasks, and Docker Compose provides PostgreSQL, Redis, and MinIO. Mock providers allow local exploration without paid APIs.

- `apps/web/` - editorial dashboard
- `apps/worker/` - background task runner
- `services/api/` - API, agents, and persistence
- `infra/` - local infrastructure

## Selection Notes

The source workspace contained additional prototypes. This public collection keeps projects with the clearest product boundary, setup instructions, and verification path. Private data, local environments, generated assets, compiled applications, and experimental duplicates were deliberately omitted.
