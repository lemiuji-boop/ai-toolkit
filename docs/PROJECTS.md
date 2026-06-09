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

## KTO AI Rewriter

A portable AI rewriting editor with an Electron shell, a local Node.js server, admin-managed provider settings, and Windows helper scripts for checking the environment and building a portable executable.

- `server.js` - provider configuration, admin sessions, and rewrite API
- `main.js` - Electron entry point
- `index.html` - browser UI
- `*.cmd` - Windows launch, diagnostics, and packaging helpers

## CED

A document/catalog processing platform with separate backend, web client, desktop client, deployment scripts, and an AI-agent service. Docker Compose and LAN/server deployment variants are included for local and networked setups.

- `backend/` - FastAPI service, migrations, workers, and tests
- `web_client/` - Vue/Vite web interface
- `desktop_client/` - .NET desktop and gateway components
- `ai_agent/` - auxiliary AI-agent service
- `docs/deployment/` - deployment runbooks and acceptance notes

## МАТНОРМ (MCC) — vertical slice

On-premise каркас «чертёж + 3D → нормы расхода → Excel»: OCR/vision через Ollama,
геометрия STEP (cadquery), детерминированный расчёт по `rules.json`, RAG-скаффолд
нормативов, Office.js-надстройка. Cursor: открыть `matnorm-mcc.code-workspace` в корне
репозитория.

- `backend/` - FastAPI pipeline (`/api/jobs`, vision, geometry, calc, verify)
- `services/rag/` - RAG нормативов (ChromaDB, `/search`)
- `addin/` - Excel taskpane (Office.js)
- `docs/TZ.md`, `docs/trace.md` - ТЗ и трассировка FR→тест
- `deploy/` - nginx TLS, инструкция sideload надстройки

## AI-MATNORM

A technologist assistant for construction-document analysis, OCR/LLM extraction, KSI handling, material-norm calculations, and Excel-oriented workflows.

- `backend/` - FastAPI application, domain services, and tests
- `frontend/` - Vue 3 + TypeScript UI
- `desktop/` - Tauri desktop shell
- `infra/` - PostgreSQL, Redis, and MinIO local infrastructure
- `docs/` - technical specification, traceability, deployment, and acceptance materials

## NTI.Sbor

An Android-first application for collecting actual labor intensity of manufacturing operations, with a FastAPI backend for synchronization and administrative workflows.

- `android/` - Kotlin, Jetpack Compose, Room, and product/demo build variants
- `backend/` - FastAPI synchronization backend
- `docs/` - Android technical specification, networking, and traceability notes
- `start.sh` - local Docker-based startup helper

## Selection Notes

The source workspace contained additional prototypes. This public collection keeps projects with the clearest product boundary, setup instructions, and verification path. Private data, local environments, generated assets, compiled applications, and experimental duplicates were deliberately omitted.
