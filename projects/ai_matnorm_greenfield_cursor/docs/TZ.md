# Техническое задание: AI-МАТНОРМ

| Поле | Значение |
|---|---|
| Название продукта | AI-МАТНОРМ |
| Версия ТЗ / дата | 2.0 / 2026-06-04 |
| Автор / заказчик | NormMat / технологи КБ |
| Платформы | Web, Windows (Tauri) |
| Краткое описание | Ассистент технолога: анализ КД, КСИ, расчёт норм материалов, Excel-ведомости с проверкой человеком. |

> Исторический черновик для Cursor: [TZ_LEGACY_CURSOR.md](TZ_LEGACY_CURSOR.md). Архитектура пайплайна: [AI_PIPELINE_SPEC.md](AI_PIPELINE_SPEC.md).

---

## 2. Цель и контекст

- **Проблема.** Ручной разбор комплектов КД и расчёт норм материалов занимает часы, ошибки в обозначениях/КИМ/припусках дорого обходятся на производстве.
- **Бизнес-цель.** Сократить время подготовки ведомости материалов на один комплект КД минимум на 50% при сохранении прослеживаемости решений (источник, ревизия, аудит).
- **Аналоги и отличие.** ERP/MES и табличные макросы не дают OCR+LLM+очередь+ревизии. Оригинальность: связка извлечения фактов из чертежей, интерактивной КСИ, детерминированного калькулятора и обучения на исправлениях технолога.
- **Вне рамок (Out of scope).** PLM/ERP интеграция v1; автоматическое утверждение расчёта без технолога; мобильные клиенты Android/iOS; хранение API-ключей в браузере.

---

## 3. Пользователи и сценарии

| Роль | Контекст |
|---|---|
| Гость | Просмотр демо без изменений |
| Технолог | Загрузка КД, запуск обработки, правки, расчёт, экспорт |
| Старший технолог | Утверждение ревизий, сравнение, назначение |
| Администратор | Пользователи, ИИ-провайдеры, справочники, безопасность |

| ID | User Story |
|---|---|
| US-1 | Как технолог, я хочу загрузить комплект КД, чтобы система начала извлечение данных. → FR-010–FR-019 |
| US-2 | Как технолог, я хочу видеть ход обработки, чтобы понимать этап и ошибки. → FR-020–FR-024 |
| US-3 | Как технолог, я хочу исправить извлечённые факты, чтобы расчёт был корректным. → FR-030–FR-034 |
| US-4 | Как технолог, я хочу построить и отредактировать КСИ, чтобы отразить состав изделия. → FR-040–FR-045 |
| US-5 | Как технолог, я хочу рассчитать материалы с объяснением, чтобы обосновать нормы. → FR-050–FR-055 |
| US-6 | Как технолог, я хочу выгрузить Excel по шаблону, чтобы передать в производство. → FR-060–FR-064 |
| US-7 | Как администратор, я хочу настроить ИИ-провайдеров, чтобы использовать Ollama и внешние API. → FR-070–FR-074 |
| US-8 | Как администратор, я хочу видеть аудит и расход токенов, чтобы контролировать безопасность и затраты. → FR-080–FR-082 |

---

## 4. Глоссарий

| Термин | Определение |
|---|---|
| КД | Конструкторская документация (PDF, DOCX, XLSX, изображения, архивы) |
| КСИ | Конструкторская структура изделия (дерево сборок/деталей) |
| КИМ | Коэффициент использования материала |
| Факт | Извлечённое поле (обозначение, материал, толщина…) с source/confidence/method |
| Ревизия расчёта | Версионированный снимок данных расчёта |
| Job | Фоновая задача обработки в очереди Redis/RQ |

---

## 5. Целевые платформы и устройства

**Неприменимо:** нативные Android/iOS (v2.0).

**Web:** Chrome 120+, Firefox 120+, разрешения 1280×720, 1920×1080; масштаб шрифта 100–125%; вкладка RU.

**Desktop:** Windows 10+ (Tauri 2), подключение к серверу по HTTPS/VPN.

**Критерий приёмки:** ключевые экраны (login, dashboard, calculation workspace, review, KSI, materials, excel, admin) без горизонтального overflow и с читаемым контрастом на всех пунктах матрицы.

---

## 6. Функциональные требования (FR)

| ID | Требование | Критерий приёмки | Приоритет | US |
|---|---|---|---|---|
| FR-001 | Аутентификация email/пароль | Login возвращает JWT; неверный пароль — 401 без утечки деталей | MUST | US-1 |
| FR-002 | RBAC на защищённых API | Гость не может изменять расчёты; технолог — может в своих проектах | MUST | US-1 |
| FR-003 | Refresh токена | Refresh выдаёт новую пару токенов; просроченный refresh — 401 | MUST | US-1 |
| FR-004 | Аудит login/logout | События в audit_logs и security_events | MUST | US-8 |
| FR-010 | CRUD проектов | Создание/список/изменение проекта технологом | MUST | US-1 |
| FR-011 | CRUD расчётов и ревизий | Расчёт в проекте; новая ревизия; блокировка утверждённой | MUST | US-1 |
| FR-012 | Загрузка файлов | PDF/DOCX/XLSX/PNG/JPG/ZIP до лимита NFR-002; MIME-валидация | MUST | US-1 |
| FR-013 | Карантин и MinIO | Файл в quarantine до проверки; метаданные в БД | MUST | US-1 |
| FR-014 | Безопасная распаковка ZIP | zip-slip отклоняется тестом | MUST | US-1 |
| FR-020 | Очередь document-processing | API возвращает job_id < 2 с; worker обрабатывает | MUST | US-2 |
| FR-021 | События job (SSE) | Клиент получает progress ≥ 1 событие/этап | MUST | US-2 |
| FR-022 | Pause/resume/cancel job | Статус в БД меняется; cancel останавливает worker | MUST | US-2 |
| FR-030 | Классификация документов | Тип документа сохраняется с method/confidence | MUST | US-3 |
| FR-031 | OCR/текст PDF | Скан: OCR; текстовый PDF: text layer + OCR fallback | MUST | US-3 |
| FR-032 | Извлечение фактов | У факта есть source, confidence, method; bbox если есть | MUST | US-3 |
| FR-033 | Подтверждение/отклонение факта | PATCH/confirm/reject + user_correction | MUST | US-3 |
| FR-034 | Вопросы ассистента при низкой уверенности | question создаётся; ответ пользователя сохраняется | SHOULD | US-3 |
| FR-040 | Построение КСИ | POST build → дерево nodes в БД | MUST | US-4 |
| FR-041 | Ручное редактирование КСИ | PATCH node, add children | MUST | US-4 |
| FR-042 | Пересчёт количеств по дереву | qty propagation в API ответе | MUST | US-4 |
| FR-050 | Справочник материалов | CRUD/read materials, aliases | MUST | US-5 |
| FR-051 | Правила КИМ/припусков | kim_rules, allowance_rules применяются в калькуляторе | MUST | US-5 |
| FR-052 | Детерминированный расчёт | Результат с formula + inputs + rules version | MUST | US-5 |
| FR-053 | Вспомогательные материалы | aux rules учитываются в summary | SHOULD | US-5 |
| FR-054 | Объяснение расчёта | explanation в results API | MUST | US-5 |
| FR-060 | Загрузка Excel-шаблона | template в БД + field_mapping JSON | MUST | US-6 |
| FR-061 | Экспорт по mapping | xlsx сохраняет стили диапазона; export linked to revision | MUST | US-6 |
| FR-062 | Excel-like редактор | Редактирование ячеек на фронте; сохранение черновика | SHOULD | US-6 |
| FR-063 | Отчёт по расчёту | Report API + страница с snapshot | SHOULD | US-6 |
| FR-070 | CRUD AI-провайдеров (админ) | create/update/delete; ключ шифруется | MUST | US-7 |
| FR-071 | Проверка соединения провайдера | Ответ ≤ 5 с: valid / причина ошибки | MUST | US-7 |
| FR-072 | LLM router из БД | classify/LLM использует активного провайдера | MUST | US-7 |
| FR-073 | Fallback при сбое провайдера | Задача не теряется; fallback/mock + событие | MUST | US-7 |
| FR-074 | Журнал ai_requests | tokens, model, status без секретов | MUST | US-8 |
| FR-080 | Админ: пользователи | list/create users, roles | MUST | US-8 |
| FR-081 | Мониторинг jobs/health | postgres/redis/minio/worker статусы | MUST | US-8 |
| FR-082 | Security events UI | Список login_failed и др. | SHOULD | US-8 |
| FR-090 | RAG по подтверждённым фактам | Индекс в Qdrant; поиск эталонов | SHOULD | US-3 |
| FR-091 | Desktop: URL сервера | localStorage + sync events | SHOULD | US-1 |
| FR-092 | Backup/restore | scripts backup.sh/restore.sh документированы | MUST | US-8 |

---

## 7. Нефункциональные требования (NFR)

| ID | Категория | Требование | Целевое значение |
|---|---|---|---|
| NFR-001 | API latency | GET /health, /users/me | p95 ≤ 500 ms (local) |
| NFR-002 | Upload | max file size | ≤ 100 MB (config) |
| NFR-003 | SSE | события job | задержка ≤ 3 s от worker |
| NFR-004 | Локализация | UI | RU, UTF-8 КД |
| NFR-005 | Доступность | кнопки/поля | min touch 40px web |
| NFR-006 | Uptime worker | RQ worker | перезапуск без потери job record |
| NFR-007 | Тесты CI | backend+frontend build | pytest + npm build green |

---

## 8. Дизайн и UX

- **Токены:** `--pf-*` в [frontend/src/styles/theme.css](../frontend/src/styles/theme.css).
- **Темы:** светлая (v2.0); тёмная — COULD.
- **Ключевые экраны:** Login, Dashboard, CalculationWorkspace, Review, KSI, Materials, Excel, Admin.
- **Утверждение:** макеты/прототип согласуются до релиза major; правки в CHANGELOG UI.

**Неприменимо:** отдельное нативное mobile UI.

---

## 9. Настройки приложения

| Настройка | Кто | Хранение |
|---|---|---|
| API-ключи провайдеров | Админ | БД encrypted (ApiKeySecret) |
| Ollama base URL | Админ | AiProvider.config |
| Лимиты токенов/провайдер | Админ | AiProvider |
| URL сервера (desktop) | Пользователь | localStorage, не секрет |
| Тема UI | Пользователь | COULD localStorage |

**Критерий:** ключ не отображается полностью после сохранения; test-connection ≤ 5 с.

---

## 10. Интеграции и внешние сервисы

| Сервис | Назначение | Ошибки |
|---|---|---|
| PostgreSQL | основные данные | 503 + сообщение |
| Redis/RQ | очередь | job failed event |
| MinIO | файлы | retry upload |
| Ollama | локальный LLM | fallback |
| OpenAI-compatible API | облачный LLM | fallback, лимиты |
| Qdrant | RAG | degraded без RAG |
| Tesseract OCR | сканы | MUST; Paddle COULD |

Политика внешнего API: документы с меткой `local_only` не отправляются во внешний провайдер (SEC-010).

---

## 11. Данные

См. [DATABASE_MODEL.md](DATABASE_MODEL.md). Персональные: email пользователей, audit. Файлы КД — конфиденциальны, только в MinIO с RBAC.

Миграции: Alembic. Инварианты: immutable files, immutable approved revisions, corrections не затирают оригинал.

---

## 12. Безопасность и приватность (SEC)

| ID | Требование | Критерий приёмки |
|---|---|---|
| SEC-001 | Секреты не в репозитории/frontend | grep + .gitignore |
| SEC-002 | TLS в production | cleartext только local dev |
| SEC-003 | JWT + RBAC | тесты 401/403 |
| SEC-004 | Rate limit login/upload | middleware активен |
| SEC-005 | Шифрование API keys at rest | roundtrip encrypt/decrypt test |
| SEC-006 | Валидация LLM JSON | Pydantic reject invalid |
| SEC-007 | Нет секретов в логах | audit ai_requests |
| SEC-008 | Safe ZIP | test_validator |
| SEC-009 | CORS whitelist | config CORS_ORIGINS |
| SEC-010 | local_only policy | external provider skip |

---

## 13. Архитектура и стек

- **Backend:** FastAPI, SQLAlchemy, Alembic, RQ — [AGENTS.md](../AGENTS.md)
- **Frontend:** Vue 3, TS, Vite, Pinia
- **Desktop:** Tauri 2
- **ADR-1:** долгие задачи только через RQ, не HTTP blocking
- **ADR-2:** расчёт материалов детерминированный, LLM не подменяет формулы
- **ADR-3:** факты с evidence; LLM outputs через JSON Schema

---

## 14. Ограничения, допущения, открытые вопросы

**Ограничения:** RTX 3060 6GB для локальных моделей; VPN для доступа v1.

**Допущения:** технолог проверяет факты до расчёта; один PostgreSQL instance.

| Вопрос | Ответственный | Срок |
|---|---|---|
| Эталон Excel заказчика | Заказчик | до FR-061 UAT |
| PaddleOCR vs Tesseract only | Dev | COULD в v2.1 |
| Политика PII во внешний API | Security | до prod |

---

## 15. Критерии приёмки / Definition of Done

- [ ] Все MUST FR/NFR/SEC реализованы
- [ ] [TRACEABILITY.md](TRACEABILITY.md): каждый MUST → код + тест
- [ ] [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) пройден
- [ ] `scripts/verify.sh` green
- [ ] UAT: 10+ комплектов КД (процедура в ACCEPTANCE_CHECKLIST)

---

## 16. Этапы и поставка

См. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) (M0–M12). Поставка инкрементальная: милстоун → verify → обновление TRACEABILITY.
