# План разработки AI-МАТНОРМ (M0–M12)

Источник требований: [TZ.md](TZ.md). Трассировка: [TRACEABILITY.md](TRACEABILITY.md).

## M0 — Bootstrap

| | |
|---|---|
| FR | NFR-007 |
| Артефакт | docker compose, health, CI, `.env.example` |
| Проверка | `./scripts/verify.sh` |
| Готово когда | pytest + frontend build + compose config OK |

## M1 — Auth / RBAC

| | |
|---|---|
| FR | FR-001–FR-004, SEC-003 |
| Артефакт | login, refresh, logout, roles, seed_admin |
| Проверка | `pytest tests/test_auth.py` |

## M2 — Projects / Calculations

| | |
|---|---|
| FR | FR-010, FR-011 |
| Артефакт | projects, calculations, revisions, audit |
| Проверка | `pytest tests/test_projects.py` |

## M3 — Files / Storage

| | |
|---|---|
| FR | FR-012–FR-014, SEC-008 |
| Артефакт | upload, MinIO, quarantine, ZIP safe |
| Проверка | `pytest tests/test_validator.py` + test_files |

## M4 — Jobs / Progress

| | |
|---|---|
| FR | FR-020–FR-022, NFR-003 |
| Артефакт | RQ worker, SSE, pause/cancel |
| Проверка | `pytest tests/test_jobs.py` |

## M5 — Document Intelligence

| | |
|---|---|
| FR | FR-030–FR-034, FR-031 |
| Артефакт | pipeline, OCR config, facts evidence UI |
| Проверка | `pytest tests/test_documents.py` |

## M6 — LLM Router

| | |
|---|---|
| FR | FR-070–FR-074, SEC-006, SEC-010 |
| Артефакт | DB providers, test-connection, router factory |
| Проверка | `pytest tests/test_admin_providers.py` |

## M7 — KSI

| | |
|---|---|
| FR | FR-040–FR-042 |
| Артефакт | ksi build/patch, ksi-tree UI |
| Проверка | `pytest tests/test_ksi.py` |

## M8 — Materials

| | |
|---|---|
| FR | FR-050–FR-054 |
| Артефакт | calculator, materials UI with explanation |
| Проверка | `pytest tests/test_materials.py` |

## M9 — Excel

| | |
|---|---|
| FR | FR-060–FR-062 |
| Артефакт | field_mapping, export, excel grid |
| Проверка | `pytest tests/test_excel.py` |

## M10 — Admin / Security

| | |
|---|---|
| FR | FR-080–FR-082, SEC-001–SEC-009 |
| Артефакт | admin UI, monitoring probes, security events |
| Проверка | verify + manual admin checklist |

## M11 — RAG / Reports / Frontend routes

| | |
|---|---|
| FR | FR-063, FR-090, FR-091 |
| Артефакт | Qdrant RAG, ReportPage, router cleanup |
| Проверка | `pytest tests/test_rag.py` (optional skip if no Qdrant) |

## M12 — Desktop / Hardening

| | |
|---|---|
| FR | FR-091, FR-092 |
| Артефакт | Tauri settings, backup/restore docs |
| Проверка | DEPLOYMENT.md + verify.sh |

## Промпты Cursor

Индекс: [prompts/MILESTONE_INDEX.md](../prompts/MILESTONE_INDEX.md)
