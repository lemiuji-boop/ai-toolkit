# Чек-лист приёмки AI-МАТНОРМ v2.0

## Автоматическая проверка

```bash
./scripts/verify.sh
```

## §15 TZ — Definition of Done

- [ ] Все MUST FR из [TZ.md](TZ.md) — статус `done` в [TRACEABILITY.md](TRACEABILITY.md)
- [ ] Каждый MUST FR имеет pytest или e2e-manual шаг
- [ ] [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) — пункты MUST отмечены
- [ ] Frontend build без ошибок
- [ ] Login + сквозной сценарий (см. UAT ниже)

## Промышленная версия (legacy §25)

- [ ] 10+ комплектов КД через UAT (процедура ниже)
- [ ] Технолог правит факты до расчёта
- [ ] КСИ редактируется
- [ ] Материалы с explanation
- [ ] Excel по шаблону с mapping
- [ ] Админ: провайдеры + test-connection ≤ 5 с
- [ ] Ollama fallback + внешний API из админки
- [ ] Job не теряется при сбое провайдера
- [ ] SSE прогресс на UI
- [ ] Backup/restore документирован и проверен
- [ ] Windows Tauri подключается к серверу

## UAT — 10+ комплектов КД

1. Подготовить папки в `datasets/samples/` (не коммитить конфиденциальные PDF в git без согласования).
2. Для каждого комплекта: создать проект → расчёт → загрузить файлы → job → review фактов → KSI → materials → export Excel.
3. Фиксировать в таблице: ID комплекта | время | ошибки | % фактов без правки.

| # | Комплект | Дата | Результат | Примечание |
|---|----------|------|-----------|------------|
| 1 | | | | |

## Security quick audit

```bash
# нет секретов в frontend
rg -i "api[_-]?key|secret|password\s*=" frontend/src --glob '!node_modules'
# .env не в git
git check-ignore -v .env
```
