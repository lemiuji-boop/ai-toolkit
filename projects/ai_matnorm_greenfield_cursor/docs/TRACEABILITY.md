# Матрица трассировки FR → код → тест

Статусы: `done` | `partial` | `stub`. Обновлено: 2026-06-04.

| FR-ID | Pri | Статус | Модули | Тест |
|-------|-----|--------|--------|------|
| FR-001 | MUST | done | auth.py | test_auth.py |
| FR-002 | MUST | done | permissions.py | test_auth.py |
| FR-003 | MUST | done | auth.py | test_auth.py |
| FR-004 | MUST | done | audit.py | test_auth.py |
| FR-010 | MUST | done | projects.py | test_projects.py |
| FR-011 | MUST | done | calculations.py | test_projects.py |
| FR-012 | MUST | done | files.py, validator.py | test_files.py, test_validator.py |
| FR-013 | MUST | done | storage/s3.py | manual / compose |
| FR-014 | MUST | done | validator.py | test_validator.py |
| FR-020 | MUST | done | jobs.py, tasks.py | test_jobs.py |
| FR-021 | MUST | done | jobs.py SSE | test_jobs.py |
| FR-022 | MUST | done | jobs.py cancel + RQ | test_jobs.py |
| FR-030 | MUST | done | document_classifier.py | test_documents.py |
| FR-031 | MUST | done | ocr/provider.py, config OCR_PROVIDER | test_documents.py |
| FR-032 | MUST | done | ExtractedFact + schemas | test_documents.py |
| FR-033 | MUST | done | documents.py | test_documents.py |
| FR-034 | SHOULD | partial | assistant.py | manual |
| FR-040 | MUST | done | ksi.py, ksi_builder.py | test_ksi.py |
| FR-041 | MUST | done | ksi.py | test_ksi.py |
| FR-042 | MUST | done | ksi_builder qty | test_ksi.py |
| FR-050 | MUST | done | materials.py | test_materials.py |
| FR-051 | MUST | done | kim/allowance rules | test_materials.py |
| FR-052 | MUST | done | material_calculator.py | test_materials.py |
| FR-053 | SHOULD | partial | aux rules | manual |
| FR-054 | MUST | done | formula in items | test_materials.py |
| FR-060 | MUST | done | templates.py | test_excel.py |
| FR-061 | MUST | done | excel_templates/export.py | test_excel.py |
| FR-062 | SHOULD | done | ExcelEditorPage localStorage draft | manual |
| FR-063 | SHOULD | done | reports.py, ReportPage.vue | manual |
| FR-070 | MUST | done | admin.py CRUD | test_admin_providers.py |
| FR-071 | MUST | done | test-connection | test_admin_providers.py |
| FR-072 | MUST | done | llm_router/factory.py | test_admin_providers.py |
| FR-073 | MUST | done | router fallback | test_admin_providers.py |
| FR-074 | MUST | done | AiRequest | test_admin_providers.py |
| FR-080 | MUST | done | admin users | test_admin_providers.py |
| FR-081 | MUST | done | monitoring.py | test_monitoring.py |
| FR-082 | SHOULD | done | AdminPage security list | manual |
| FR-090 | SHOULD | partial | rag.py Qdrant HTTP | test_rag.py |
| FR-091 | SHOULD | done | SettingsPage, sync.store | manual |
| FR-092 | MUST | done | scripts/backup.sh | verify.sh |

Прогон: `cd backend && pytest -q` (22+ tests), `./scripts/verify.sh`.
