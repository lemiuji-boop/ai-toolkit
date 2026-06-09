# context — текущая итерация

## Текущая задача
- Состояние: каркас развёрнут и запущен (M1). Идёт реализация FR по очереди CURSOR_РАБОТА.md §4.

## Что трогать
- По одному модулю за итерацию: `app/services/vision.py`+`ocr.py`, затем `geometry.py`/`calc.py`, затем `rules.json`, затем новый `services/rag/`.

## Что НЕ трогать
- Публичный API: `app/core/schemas.py` (без согласованного расширения), роуты `app/api/*`.

## Ссылки
- ТЗ: `docs/TZ.md`
- Правила: `.cursor/rules/*.mdc`, `CLAUDE.md`
- Трассировка: `docs/trace.md`
