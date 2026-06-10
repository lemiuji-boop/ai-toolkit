# Трассировка FR → код → тест

Без строки трассировки FR считается невыполненным (правило приёмки, документ 01/02).

| FR | Описание | Файл реализации | Тест |
|---|---|---|---|
| FR-001 | POST /api/jobs | `backend/app/api/jobs.py` | `backend/tests/test_health.py::test_job_runs_without_model_or_llm` |
| FR-002 | OCR-препроцесс зон, PDF→PNG | `backend/app/services/ocr.py` | `backend/tests/test_vision.py` |
| FR-003 | Уверенность по полям | `backend/app/services/vision.py` | `backend/tests/test_vision.py` |
| FR-004 | Нераспознанное → null | `backend/app/services/vision.py` | `backend/tests/test_vision.py` |
| FR-007 | /health, /version | `backend/app/api/health.py` | `backend/tests/test_health.py::test_health` |
| FR-010 | Геометрия из STEP + дерево | `backend/app/services/geometry.py` | `backend/tests/test_assembly.py` |
| FR-011 | Расчёт норм по правилам | `backend/app/services/calc.py` | `backend/tests/test_calc.py` |
| FR-012 | Сверка чертёж ↔ 3D | `backend/app/services/verify.py` | `backend/tests/test_calc.py` (косвенно), `test_assembly.py` |
| FR-013 | Нормоконтроль | `backend/app/services/calc.py::normcontrol` | `backend/tests/test_calc.py` |
| FR-014 | Входимость на с/к | `backend/app/services/calc.py::build_rows` | `backend/tests/test_assembly.py` |
| FR-015 | Виды заготовки | `backend/app/data/rules.json`, `backend/app/services/calc.py` | `backend/tests/test_calc_zagotovki.py` |
| FR-016 | Гибкая загрузка: drawing_only / model_only / paired, `mode` query, `data_completeness` | `backend/app/api/jobs.py`, `backend/app/core/schemas.py`, `backend/app/services/verify.py` | `backend/tests/test_job_modes.py` |
| ADM-001 | Админ-панель: мониторинг сервисов, метрики GPU/хоста, журнал заданий (без обозначений); персистентность `data/admin/jobs.jsonl` + импорт `data/exports/jobs/` | `backend/app/api/admin.py`, `backend/app/services/admin_monitor.py`, `backend/app/services/job_store.py`, `admin/` | `backend/tests/test_admin.py` |
| EXP-001 | Пакетный экспорт КД: JSON/CSV, деревья, сводка материалов (`data/exports/`) | `scripts/export_analyze.py`, `scripts/export-and-analyze.sh` | ручной прогон + `report_summary.json` |
| ADD-001 | Excel add-in sideload + Cloudflare tunnel + единый origin `/addin/` | `addin/`, `scripts/start-tunnel.sh`, `scripts/start-matnorm-stack.sh`, `scripts/package-addin.sh`, `backend/app/main.py` | `addin/dist/manifest.xml`, `addin/matnorm-addin.zip` |
| RAG-FR-001 | Индексация нормативов (`POST /index`, `POST /ingest`) | `services/rag/app/main.py`, `services/rag/app/core/ingest.py`, `services/rag/app/store.py` | `services/rag/tests/test_rag.py::test_index_adds_documents`, `test_ingest_markdown_file` |
| RAG-FR-002 | Семантический поиск (`POST /search`) | `services/rag/app/main.py`, `services/rag/app/store.py`, `services/rag/app/core/embed.py` | `services/rag/tests/test_rag.py::test_search_returns_hits_with_source` |
| RAG-FR-003 | Цитирование источника (`source` у hit) | `services/rag/app/core/schemas.py`, `services/rag/app/store.py` | `services/rag/tests/test_rag.py::test_search_returns_hits_with_source` |
| RAG-FR-004 | `/health`, `/version` RAG | `services/rag/app/main.py` | `services/rag/tests/test_rag.py::test_health_and_version` |
| RAG-INT-001 | Прокси `POST /api/rag/search` (§14 — вне MUST FR монолита) | `backend/app/api/rag.py`, `backend/app/services/rag_client.py` | `backend/tests/test_rag_proxy.py` |
| FR-060 | Модели БД (15 таблиц §4 TZ-FINAL) | `backend/app/db/models.py`, `backend/app/db/session.py` | `backend/tests/test_db_schema.py` |
| FR-063 | Версионируемые rules.json (`version` обязателен) | `backend/app/services/rules_registry.py`, `backend/app/data/rules.json` | `backend/tests/test_rules_registry.py` |
| FR-070/071 | Асинхронные задания: POST 202, GET статус, SSE этапов | `backend/app/api/jobs.py`, `backend/app/services/jobs_runner.py` | `backend/tests/test_jobs_runner.py`, `backend/tests/test_health.py` |
| FR-080 | Слой LLMProvider (base/ollama/openai_compat) | `backend/app/services/llm/*` | `backend/tests/test_llm_structured.py` |
| FR-081 | Маршрутизатор confidential→local only | `backend/app/services/llm/router.py`, `backend/app/services/llm/registry.py` | `backend/tests/test_llm_router.py`, `backend/tests/test_health.py::test_job_returns_503_when_no_local_provider` |
| FR-082 | Vision без заглушек: structured call + явные ошибки | `backend/app/services/vision.py` | `backend/tests/test_vision.py` |
| FR-093 | Правило версий actual/archive (чистая логика) | `backend/app/services/versioning.py` | `backend/tests/test_versioning.py` |
| T-00 | Гейт запрещённых паттернов (stub/TODO в app/) | `scripts/ci-stub-gate.sh` | ручной прогон `bash scripts/ci-stub-gate.sh` |
| T-08 | CRUD провайдеров ИИ: пресеты, шифрование ключей, маскирование, test-connection без egress (SEC-001) | `backend/app/services/providers_store.py`, `backend/app/api/admin.py` | `backend/tests/test_providers_api.py` |
| T-08 | Реестр провайдеров из хранилища админки (fallback env-Ollama) | `backend/app/services/llm/registry.py` | `backend/tests/test_providers_api.py::test_confidential_routing_ignores_external` |
| — | Мониторинг подключений клиентов (/api/admin/clients, SEC-002) | `backend/app/services/clients_monitor.py`, `backend/app/main.py` | `backend/tests/test_clients_api.py` |
| T-08+ | Внешние провайдеры (egress разрешён 2026-06-10): OpenAI-совместимый путь + Anthropic Messages API | `backend/app/services/llm/openai_compat.py`, `backend/app/services/llm/anthropic.py`, `backend/app/services/providers_store.py` | `backend/tests/test_llm_external.py` |
| T-16 (часть, FR-043) | JWT-аутентификация: `POST /api/auth/login`, защита `/api/admin/*`, форма входа в админ-панели | `backend/app/api/auth.py`, `backend/app/services/sessions.py`, `backend/app/api/admin.py`, `admin/*` | `backend/tests/test_auth.py` |
| T-02/T-03 (часть) | Postgres в compose + create_all на старте (Alembic — открытая задача) | `docker-compose.yml`, `backend/app/db/session.py`, `backend/app/main.py` | `backend/tests/test_db_schema.py`, ручная проверка `/health` на Postgres |
