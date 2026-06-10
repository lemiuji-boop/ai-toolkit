# Открытые вопросы (TZ-FINAL §8)

Заполняется при СТОП-протоколе; не решается угадыванием.

| Дата | Задача | Что неизвестно | Что заблокировано | Варианты |
|---|---|---|---|---|
| 2026-06-10 | T-02 | Версия Alembic в среде развёртывания | Автогенерация миграции `initial schema` | Зафиксировать alembic в pyproject §5 или генерировать в CI |
| 2026-06-10 | T-03 | Адреса MinIO/Postgres в compose продакшена | `/ready` с проверкой MinIO | Уточнить у сетевого администратора имена сервисов docker-compose |
| 2026-06-10 | §14 (TZ.md) | TLS/mixed content для Excel add-in | Единый origin `https://matnorm.lan` vs tunnel | LAN-сертификат (deploy/certs) или Cloudflare tunnel — согласовать с ИБ |
| 2026-06-10 | деплой | GitHub PAT истёк | `git push` (4 коммита + ~95 файлов не запушены) | Пользователь обновляет PAT (Contents: write), затем `scripts/gh-auth-push.sh` |
| 2026-06-10 | T-08 / SEC-001 | ~~Разрешён ли исходящий egress к внешним ИИ-API (Claude/OpenAI/DeepSeek/MiMo/Kimi) для НЕконфиденциальных задач~~ **РЕШЕНО 2026-06-10 (решение пользователя):** egress разрешён для неконфиденциальных задач — `ALLOW_EXTERNAL_PROVIDERS=1`. Конфиденциальные (КД) по-прежнему только kind=local (FR-081, тест границы) | — | Реализовано: OpenAI-совместимый путь (openai/deepseek/mimo/kimi) + Anthropic Messages API (claude); тесты `tests/test_llm_external.py` |
| 2026-06-10 | T-03 | ~~Выбор DATABASE_URL для пилота~~ **РЕШЕНО 2026-06-10 (решение пользователя):** Postgres-контейнер в compose (`postgres:16-alpine`, том `pgdata`, healthcheck). Хост-бэкенд → `localhost:5432`. Схема создаётся `create_all` на старте; **Alembic (T-02/T-03) по-прежнему не настроен** — миграции остаются открытой задачей | Перевод job_store/providers с JSON-файлов на БД — отдельная задача | sqlite-фолбэк сохранён для тестов |
| 2026-06-10 | T-03 | Нужен ли MinIO в пилоте (хранение сканов/кропов) | Поля `scan_object_key`/`crop_object_key`, `/ready` с пробой MinIO | (а) без MinIO — файловая система; (б) MinIO-контейнер в compose |
| 2026-06-10 | T-06 | ~~Требования к аутентификации админки и API на пилоте~~ **РЕШЕНО 2026-06-10 (решение пользователя):** JWT (T-16): `POST /api/auth/login` → `{token}` по env ADMIN_USER/ADMIN_PASSWORD; `/api/admin/*` защищены Bearer JWT; `/health`, `/version`, `/api/jobs`, `/addin` открыты (контракт §4 — надстройка Excel). Полный T-16 (bcrypt + таблица users + журнал sessions + вход в надстройке) — остаётся в плане | — | Тесты: `tests/test_auth.py` |
