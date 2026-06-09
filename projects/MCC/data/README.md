# Данные МАТНОРМ (MCC)

## Структура каталогов

```text
data/
├── drawing.png          # синтетика для smoke-теста
├── part.step            # синтетика STEP (бокс 180×90×24 мм)
├── incoming/
│   ├── drawings/        # только чертежи (режим drawing_only)
│   ├── models/          # только STEP/STP (режим model_only)
│   └── pairs/           # пары с одинаковым базовым именем (режим paired)
└── examples/
    └── calc/            # примеры расчётов / эталонные xlsx (по мере появления)

examples/
└── calc/                # дубликат каталога примеров на корне проекта
```

## Режимы API `POST /api/jobs`

| Режим (`?mode=`) | Файлы | Поведение |
|------------------|-------|-----------|
| `auto` (по умолчанию) | 1 или 2 | оба → `paired`; только чертёж → `drawing_only`; только 3D → `model_only` |
| `drawing_only` | `drawing` | OCR/VLM + заглушка геометрии; сверка чертёж↔3D **не выполняется** |
| `model_only` | `model3d` | STEP/cadquery; поля с чертежа из 3D; сверка **не выполняется** |
| `paired` | оба | полный конвейер + перекрёстная сверка |

Минимум **один** файл обязателен; иначе HTTP 422.

## Куда класть входящие КД

- **Пара «чертёж + STEP»** с одним именем, например `АБВГ.001.001.pdf` и `АБВГ.001.001.step` → `incoming/pairs/`
- **Только чертежи** → `incoming/drawings/`
- **Только 3D** → `incoming/models/`

## Запуск

```bash
# Авто-режим по наличию файлов
./scripts/run-pipeline.sh --drawing data/drawing.png --model data/part.step
./scripts/run-pipeline.sh --drawing data/incoming/drawings/деталь.pdf
./scripts/run-pipeline.sh --model data/incoming/models/деталь.step

# Сканирование папки (пары по базовому имени)
./scripts/run-pipeline.sh --folder data/incoming/pairs
./scripts/ingest-folder.sh data/incoming/pairs
DRY_RUN=1 ./scripts/ingest-folder.sh /path/to/комплект
```

Конфиденциальные файлы **не коммитить** — содержимое `incoming/*` в `.gitignore`.
