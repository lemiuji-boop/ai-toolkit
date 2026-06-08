# НТИ.Сбор

Мобильное Android-приложение для сбора фактической трудоёмкости технологических операций.

## Структура

- `android/` — Kotlin, Jetpack Compose, Room
- `backend/` — FastAPI приёмник синхронизации (dev/MVP)
- `docs/` — ТЗ, API, трассировка FR

## Быстрый старт

```bash
# Всё одной командой (Docker: API + админка)
./start.sh

# С HTTPS-туннелем для телефона через интернет
./start.sh --tunnel

# Локально без Docker
cd backend && ./scripts/run_dev.sh
```

- Админка: http://127.0.0.1:8010/admin/login — `admin` / `admin123`
- Приложение: `ivanov` / `demo123` — см. `docs/NETWORK_SETUP.md`
- Тесты: `cd backend && .venv/bin/pip install -e ".[dev]" && .venv/bin/pytest -q`

# Android — production (дизайн v2, вход на сервере)
cd android && ./gradlew :app:assembleProdDebug
# Установка: adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk

# 4 варианта дизайна для согласования (полнофункциональные)
cd android && ./scripts/install_demo_all.sh
```

| Сборка | applicationId | Название |
|--------|---------------|----------|
| v1 | ru.nti.sbor.demo1 | НТИ.Сбор 1 — светлый главный |
| v2 | ru.nti.sbor.demo2 | НТИ.Сбор 2 — тёмный главный |
| v3 | ru.nti.sbor.demo3 | НТИ.Сбор 3 — стиль формы |
| v4 | ru.nti.sbor.demo4 | НТИ.Сбор 4 — стиль настроек |
| prod | ru.nti.sbor | НТИ.Сбор (релиз) |

Документация: [docs/TZ_Android_sbor_trudoemkosti.md](docs/TZ_Android_sbor_trudoemkosti.md)
