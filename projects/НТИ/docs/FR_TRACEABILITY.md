# Трассировка FR → код → тест

| ID | Код | Тест |
|----|-----|------|
| FR-001 | `RecordFormViewModel`, `LaborRepository.createRecord` | Instrumented (manual) |
| FR-002 | `RecordFormScreen` OperationDropdown | UI |
| FR-003 | `RecordValidator` | `RecordValidatorTest` |
| FR-004 | `NtiDatabase`, `LaborRepository` | Instrumented offline |
| FR-005 | `HomeScreen` / `HomeScreenV1` / `HomeScreenV2`, `RecordDao.observeAll` | UI |
| FR-006 | `HomeScreen` delete dialog | UI |
| FR-007 | `RecordFormViewModel` edit | UI |
| FR-008 | `CsvExporter`, `ExportShareManager` | `CsvExporterTest` |
| FR-009 | `SettingsViewModel.saveProfile` | UI |
| FR-010 | `HomeViewModel.onSearchChange` | UI |
| FR-011 | `LaborSummaryCalculator` | `LaborSummaryTest`, `UnitConverterTest` |
| FR-012 | `SettingsViewModel.clearAllData` | UI |
| FR-013 | `SyncRepository`, `backend/app/api/mobile.py` | Manual + MockWebServer |
| FR-014 | `CsvExporter.parseOperationsCsv`, `pullOperations` | `CsvExporterTest` |

## SEC

| ID | Реализация |
|----|------------|
| SEC-001 | `AndroidManifest` — только INTERNET |
| SEC-002 | Room в private app storage |
| SEC-003 | `network_security_config.xml`, HTTPS |
| SEC-004 | `SecureServerSettings` |
| SEC-005 | Release: no PII in logs (no custom Log calls) |
| SEC-007 | FR-008, FR-012 в настройках |
