# Тестовые и входящие КД

## Синтетика (smoke-тест)
- `drawing.png` — минимальный PNG для проверки заглушки/конвейера
- `part.step` — бокс 180×90×24 мм для cadquery

## Входящие файлы от пользователя
Положите пару «чертёж + STEP» в каталог **`incoming/`**:

```text
data/incoming/
├── ваш_чертёж.pdf    # или .png / .jpg
└── ваш_деталь.step   # или .stp
```

Запуск конвейера:

```bash
./scripts/run-pipeline.sh data/incoming/ваш_чертёж.pdf data/incoming/ваш_деталь.step
```

Или целая папка (если в ней ровно один PDF/PNG и один STEP):

```bash
FOLDER=/path/to/комплект
DRAW=$(find "$FOLDER" -maxdepth 1 -type f \( -iname '*.pdf' -o -iname '*.png' -o -iname '*.jpg' \) | head -1)
STEP=$(find "$FOLDER" -maxdepth 1 -type f \( -iname '*.step' -o -iname '*.stp' \) | head -1)
./scripts/run-pipeline.sh "$DRAW" "$STEP"
```

Конфиденциальные файлы **не коммитить** — `incoming/*` в `.gitignore` (кроме `.gitkeep`).
