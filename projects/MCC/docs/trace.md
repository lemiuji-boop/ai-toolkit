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
