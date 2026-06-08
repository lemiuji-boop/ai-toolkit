# Техническое задание для Cursor: AI-МАТНОРМ GREENFIELD

**Документ:** `docs/AI_MATNORM_GREENFIELD_TZ.md`
**Назначение:** дать Cursor полное задание на разработку всего стека с нуля.
**Статус:** greenfield-разработка, старый MVP использовать только как источник идей, но не как основу архитектуры.
**Целевая система:** веб-панель + Windows-приложение + backend + БД + OCR/LLM/агентный слой + Excel-совместимость + админка + безопасность.

---

## 1. Короткая суть проекта

`AI-МАТНОРМ` — система-ассистент технолога для анализа конструкторской документации и автоматизированного расчёта норм материалов.

Пользователь загружает комплект КД: PDF, DOC/DOCX, XLS/XLSX, изображения, сканы, архивы. Система определяет тип каждого документа, извлекает данные, связывает документы в структуру изделия, строит КСИ, рассчитывает основные и вспомогательные материалы, формирует подробный отчёт и Excel-ведомости по загруженным шаблонам.

Система должна работать интерактивно: показывать ход выполнения, комментировать свои действия, задавать вопросы при сомнениях, принимать исправления пользователя, сохранять ревизии и накапливать эталонные примеры для дальнейшего улучшения качества.

---

## 2. Главный режим разработки для Cursor

Cursor должен разрабатывать проект **с нуля** по этому ТЗ.

Запрещено:

- делать монолитный файл `main.py` со всей логикой;
- писать заглушки вместо реальных модулей без явной пометки `TODO_NOT_READY`;
- смешивать backend, frontend, OCR, LLM и расчёты в одном слое;
- хранить результаты только в памяти;
- делать расчёт без сохранения источников, уверенности и следов принятия решений;
- делать один долгий HTTP-запрос на обработку большого комплекта КД;
- считать автоматический вывод системы окончательным без этапа проверки технологом;
- хранить API-ключи в frontend или в открытом виде;
- подключать внешние ИИ-сервисы без аудита, лимитов и журналирования.

Обязательно:

- после каждого этапа проект должен запускаться;
- backend должен иметь тесты;
- frontend должен собираться;
- миграции БД должны быть воспроизводимыми;
- все долгие операции должны идти через очередь задач;
- ход работы должен отображаться через WebSocket или SSE;
- каждый извлечённый факт должен иметь `source`, `confidence`, `method`, `bbox` при наличии координат;
- любые спорные данные должны попадать в очередь вопросов пользователю.

---

## 3. Целевая инфраструктура

### 3.1. Временный сервер первого этапа

Первый этап развёртывания выполняется на ноутбуке:

```text
Lenovo Legion 5
GPU: NVIDIA RTX 3060 6 GB VRAM
ОС: Ubuntu / Linux
Локальные модели: Ollama
Внешние ИИ-сервисы: через API-провайдеры
Доступ клиентов: через VPN + web URL / desktop app
```

### 3.2. Целевая инфраструктура сервера

```text
Nginx / Caddy reverse proxy
FastAPI backend
Worker service для OCR/LLM/расчётов
PostgreSQL
Redis
MinIO/S3-compatible object storage
Qdrant/pgvector для поиска по документам и эталонам
Ollama на сервере или отдельной машине
Frontend web app
Tauri Windows app
Admin panel
Monitoring/logging
Backup service
```

### 3.3. Почему нужны очереди задач

Обработка КД, OCR, анализ изображений и LLM-вызовы могут занимать минуты. Поэтому нельзя выполнять весь процесс в одном HTTP-запросе. API должен быстро принять файлы, создать задачу и вернуть `job_id`, а обработка должна идти в worker-процессе.

---

## 4. Роли пользователей и права

### 4.1. Гость

Права:

- просмотр разрешённых демо-расчётов;
- просмотр отчётов без права изменения;
- отсутствие доступа к базе эталонов;
- отсутствие доступа к API-ключам, настройкам ИИ и админке.

### 4.2. Технолог

Права:

- создание проектов;
- загрузка КД;
- запуск распознавания;
- запуск расчёта;
- ручная корректировка распознанных данных;
- создание новых ревизий расчётов;
- экспорт Excel/отчётов;
- ответы на вопросы ассистента;
- сохранение исправлений как обучающих примеров, если разрешено политикой проекта.

### 4.3. Старший технолог / проверяющий

Права технолога плюс:

- утверждение расчётов;
- блокировка ревизий;
- сравнение ревизий;
- назначение расчёта другому технологу;
- утверждение эталонных примеров для базы знаний.

### 4.4. Администратор

Права:

- все действия пользователей;
- добавление/удаление пользователей;
- назначение ролей;
- настройка ИИ-провайдеров;
- настройка локальных моделей Ollama;
- просмотр расхода токенов;
- просмотр очередей задач;
- просмотр логов безопасности;
- настройка резервного копирования;
- настройка шаблонов Excel;
- управление справочниками материалов, КИМ, припусков и технологических правил.

---

## 5. Основные входные данные

Система должна принимать:

```text
PDF: .pdf
Word: .doc, .docx
Excel: .xls, .xlsx
Images: .png, .jpg, .jpeg, .tif, .tiff, .webp
Archives: .zip, .7z, .rar при наличии безопасного обработчика
Other: добавлять через модуль адаптеров
```

Типы документов:

- чертёж детали;
- сборочный чертёж;
- спецификация;
- ведомость материалов;
- технические требования;
- извещение об изменении;
- паспорт;
- шаблон Excel;
- произвольный сопроводительный документ.

Документы могут быть:

- с текстовым слоем;
- сканами;
- фотографиями;
- частично повреждёнными;
- с разными ориентациями страниц;
- с русским/английским текстом;
- с ошибками распознавания;
- с разными ревизиями одного изделия.

---

## 6. Что система должна извлекать из КД

Для каждого документа система должна определить:

```text
document_id
file_id
document_type
is_scan
has_text_layer
language
page_count
quality_score
revision
change_notice_number
related_designations
```

Из основной надписи и текста:

```text
designation
name
material
mass
scale
format
sheet_number
total_sheets
developer
checker
approver
revision
change_notice_number
```

Из чертежа:

```text
dimensions
overall_dimensions
thicknesses
diameters
radii
holes
bends
welds
coatings
surface_finish
heat_treatment
technical_requirements
manufacturing_hints
```

Из спецификации:

```text
position
zone
format
designation
name
quantity
note
section
parent_designation
child_designation
```

Из требований:

```text
material_constraints
coating_constraints
adhesive_constraints
sealant_constraints
process_constraints
fire_safety_constraints
quality_control_constraints
```

Каждый факт хранить в виде:

```json
{
  "field": "material",
  "value": "АМг6М ГОСТ ...",
  "normalized_value": "АМг6М",
  "source_file_id": "...",
  "source_page": 1,
  "bbox": [x1, y1, x2, y2],
  "method": "text_layer | ocr | layout | llm | rule | manual",
  "confidence": 0.0,
  "evidence_text": "Материал: АМг6М...",
  "is_user_corrected": false,
  "created_by": "system"
}
```

---

## 7. Общий пользовательский процесс

```text
1. Пользователь входит в систему.
2. Создаёт проект.
3. Создаёт расчёт или открывает существующий.
4. Загружает комплект КД.
5. Система безопасно принимает файлы и создаёт job.
6. Система классифицирует документы.
7. Система извлекает текст, таблицы, изображения, зоны и признаки чертежей.
8. Система распознаёт обозначения, наименования, материалы, массу, размеры, требования.
9. Система связывает документы по обозначениям и спецификациям.
10. Система предлагает пользователю структуру сборки.
11. Пользователь подтверждает или исправляет структуру.
12. Система строит КСИ.
13. Система анализирует технологию изготовления по признакам детали.
14. Система рассчитывает основные и вспомогательные материалы.
15. Система показывает сомнительные места и задаёт вопросы.
16. Пользователь исправляет данные или подтверждает допущения.
17. Система пересчитывает затронутые участки.
18. Система формирует отчёт и Excel-ведомости по шаблону.
19. Пользователь сохраняет ревизию.
20. При необходимости расчёт утверждается старшим технологом.
```

---

## 8. Ход работы в реальном времени

В интерфейсе должен быть экран «Ход обработки».

Он показывает:

```text
Текущий этап
Процент выполнения
Список документов
Статус каждого документа
Извлечённые факты
Ошибки и предупреждения
Вопросы ассистента
Расход токенов/моделей
Лог действий
Кнопки: Пауза / Продолжить / Остановить / Задать вопрос / Исправить
```

События передаются через WebSocket или SSE.

Пример событий:

```json
{"type":"job_started","job_id":"..."}
{"type":"file_classified","file":"A.pdf","document_type":"assembly_drawing"}
{"type":"ocr_progress","file":"A.pdf","page":2,"pages":5}
{"type":"fact_extracted","field":"mass","value":"0.245 кг","confidence":0.82}
{"type":"question_required","question":"Материал распознан как АМг6 или АМг6М. Уточните."}
{"type":"calculation_updated","materials_count":12}
{"type":"job_completed","result_id":"..."}
```

---

## 9. Архитектура модулей backend

```text
backend/
  app/
    main.py
    api/
      v1/
        auth.py
        users.py
        projects.py
        files.py
        jobs.py
        documents.py
        extraction.py
        ksi.py
        calculations.py
        materials.py
        templates.py
        reports.py
        admin.py
        ai_providers.py
        monitoring.py
    core/
      config.py
      security.py
      logging.py
      permissions.py
      audit.py
    db/
      session.py
      models.py
      repositories/
      migrations/
    services/
      file_ingestion/
      document_classifier/
      text_extraction/
      ocr/
      layout_analysis/
      drawing_understanding/
      llm_router/
      fact_extraction/
      assembly_linker/
      ksi_builder/
      process_analyzer/
      material_calculator/
      excel_templates/
      report_builder/
      feedback_learning/
      sync/
    workers/
      celery_app.py или rq_app.py
      tasks.py
    schemas/
    tests/
```

---

## 10. Архитектура frontend

```text
frontend/
  src/
    app/
    pages/
      LoginPage.vue
      DashboardPage.vue
      ProjectPage.vue
      CalculationPage.vue
      UploadPage.vue
      ProcessingPage.vue
      ReviewPage.vue
      KsiPage.vue
      MaterialsPage.vue
      ExcelEditorPage.vue
      ReportPage.vue
      AdminPage.vue
    components/
      file-upload/
      document-viewer/
      drawing-viewer/
      fact-table/
      assistant-panel/
      job-progress/
      ksi-tree/
      materials-grid/
      excel-like-grid/
      audit-log/
      admin/
    stores/
      auth.store.ts
      project.store.ts
      calculation.store.ts
      job.store.ts
      settings.store.ts
    api/
      client.ts
      auth.api.ts
      projects.api.ts
      files.api.ts
      jobs.api.ts
      calculations.api.ts
      admin.api.ts
    router/
    styles/
```

Frontend должен быть совместим с web-режимом и Tauri desktop.

---

## 11. Windows-приложение

Windows-приложение делать на Tauri.

Назначение:

- запускать тот же frontend, что и web;
- подключаться к серверу по URL;
- хранить локальный кеш пользователя;
- автоматически синхронизировать изменения при появлении связи;
- поддерживать уведомления о завершении задач;
- не хранить API-ключи ИИ-провайдеров у пользователя;
- работать через VPN-соединение или корпоративную сеть.

Структура:

```text
desktop/
  src-tauri/
  README.md
```

На первом этапе Tauri создаётся после готовности web frontend.

---

## 12. База данных

Использовать PostgreSQL.

Основные таблицы:

```text
users
roles
permissions
user_roles
projects
calculations
calculation_revisions
files
documents
pages
extracted_facts
spec_rows
assembly_links
ksi_nodes
materials
material_aliases
kim_rules
allowance_rules
aux_material_rules
process_rules
calculation_items
calculation_summaries
excel_templates
excel_exports
reports
jobs
job_events
assistant_messages
assistant_questions
user_corrections
learning_examples
ai_providers
ai_models
ai_requests
api_key_secrets
audit_logs
security_events
sync_events
```

Обязательные принципы БД:

- все расчёты версионируются;
- исходные файлы не перезаписываются;
- каждая ревизия расчёта неизменяема после утверждения;
- все ручные исправления сохраняются отдельно;
- все AI-вызовы логируются без сохранения секретных ключей;
- каждый экспорт Excel связан с расчётом и ревизией;
- все действия пользователя попадают в audit log.

---

## 13. Хранилище файлов

Использовать S3-compatible хранилище, на первом этапе MinIO.

Хранить:

```text
исходные файлы КД
нормализованные PDF
изображения страниц
OCR JSON
layout JSON
экспортированные Excel
отчёты
логи обработки
временные артефакты с TTL
```

Нельзя хранить загруженные файлы только в локальной папке backend без учёта прав доступа и резервного копирования.

---

## 14. OCR и понимание документов

### 14.1. Пайплайн распознавания

```text
FileIngestion
  ↓
DocumentNormalizer
  ↓
DocumentClassifier
  ↓
TextLayerExtractor
  ↓
ScanDetector
  ↓
OCRService
  ↓
LayoutAnalyzer
  ↓
TableExtractor
  ↓
EngineeringFactExtractor
  ↓
LLMVerifier
  ↓
HumanReviewQueue
```

### 14.2. Документы с текстовым слоем

Для машинных PDF использовать:

- PyMuPDF;
- pdfplumber;
- извлечение таблиц;
- извлечение координат текста;
- извлечение изображений страниц.

### 14.3. Сканы и картинки

Для сканов использовать:

- рендер страниц в изображения;
- deskew;
- denoise;
- contrast normalization;
- orientation detection;
- OCR;
- layout analysis;
- table recognition;
- восстановление структуры.

### 14.4. OCR-движки

Сделать интерфейс:

```python
class OcrProvider:
    def recognize_page(self, image: bytes, options: OcrOptions) -> OcrPageResult: ...
```

Реализации:

```text
TesseractProvider
PaddleOcrProvider
CloudOcrProvider optional
ManualProvider for debug
```

### 14.5. Таблицы

Таблицы должны сохраняться в структуре:

```json
{
  "table_id": "...",
  "source_page": 1,
  "bbox": [0,0,100,100],
  "rows": [
    {"cells": [{"text":"Поз.","bbox":[...]}, {"text":"Обозначение"}]}
  ],
  "confidence": 0.78,
  "method": "pdf_table | ocr_table | llm_table"
}
```

---

## 15. LLM/ИИ-слой

### 15.1. Главный принцип

LLM не должна напрямую записывать результат расчёта как истину. Она должна:

- классифицировать документы;
- помогать извлекать факты;
- объяснять сомнительные места;
- предлагать структуру изделия;
- предлагать технологические признаки;
- формировать вопросы пользователю;
- формировать отчёт;
- проверять согласованность данных;
- возвращать только валидируемый JSON по схемам.

Окончательные расчёты выполняются детерминированным модулем `material_calculator`.

### 15.2. Подключение моделей

Система должна поддерживать:

```text
Ollama local provider
OpenAI-compatible provider
Anthropic-compatible provider
Gemini-compatible provider
Custom HTTP provider
Mock provider для тестов
```

Модели нельзя хардкодить в коде. Они настраиваются в админке.

### 15.3. Роутер ИИ-провайдеров

Создать `LlmRouter`.

Задачи:

- выбирать провайдера по типу задачи;
- учитывать доступность провайдера;
- переключаться на резервный provider при ошибке;
- учитывать лимиты токенов;
- вести журнал запросов;
- не терять пользовательскую сессию при переключении;
- возвращать унифицированный результат.

Пример профилей задач:

```text
DOCUMENT_CLASSIFICATION
OCR_TEXT_CLEANUP
TITLE_BLOCK_EXTRACTION
SPECIFICATION_EXTRACTION
DRAWING_REQUIREMENTS_EXTRACTION
ASSEMBLY_LINKING
PROCESS_HINT_ANALYSIS
MATERIAL_NORM_EXPLANATION
REPORT_GENERATION
ASSISTANT_CHAT
```

### 15.4. Последовательность ИИ-агентов

```text
1. File Intake Agent
   Проверяет файлы, типы, безопасность, группирует пакет.

2. Document Classification Agent
   Определяет тип каждого документа.

3. OCR/Layout Agent
   Запускает нужный путь: text layer или OCR.

4. Engineering Extraction Agent
   Извлекает обозначение, наименование, материал, массу, размеры, требования.

5. Specification Agent
   Извлекает строки спецификаций и связи входимости.

6. Assembly Linking Agent
   Связывает документы в единую сборочную структуру.

7. Process Analysis Agent
   Определяет предполагаемую технологию изготовления.

8. Material Norm Agent
   Подготавливает данные для расчёта материалов.
   Не выполняет окончательные формулы самостоятельно.

9. Deterministic Calculator
   Считает материалы по правилам, КИМ, припускам и справочникам.

10. Review Agent
   Ищет сомнения, противоречия и вопросы к пользователю.

11. Report Agent
   Формирует отчёт и пояснения.

12. Learning Agent
   Сохраняет исправления пользователя как эталонные примеры.
```

### 15.5. Самообучение

Под самообучением понимать не автоматическое переобучение весов модели, а управляемое накопление опыта:

```text
исправления пользователя
утверждённые расчёты
пары вопрос-ответ
правила нормирования
примеры распознавания чертежей
примеры Excel-выгрузок
ошибки и их исправления
```

Все примеры проходят статусы:

```text
candidate
reviewed
approved
rejected
archived
```

Только `approved` используется для RAG, подсказок и few-shot-примеров.

---

## 16. КСИ

КСИ — отдельный режим.

Назначение:

- построить полный конструкторский состав изделия;
- показать все уровни сборки;
- указать входимость;
- связать каждую позицию с материалами;
- рассчитать количество материалов на позицию и на верхний уровень;
- сформировать Excel/отчёт по шаблону.

Структура узла КСИ:

```json
{
  "node_id": "...",
  "parent_id": "...",
  "level": 0,
  "designation": "...",
  "name": "...",
  "node_type": "assembly | detail | standard_part | material | other",
  "quantity_per_parent": 1,
  "quantity_total": 1,
  "source_document_id": "...",
  "confidence": 0.95,
  "materials": []
}
```

Функции интерфейса КСИ:

- древовидный вид;
- таблица;
- фильтр по уровню;
- поиск по обозначению;
- раскрытие/сворачивание узлов;
- ручное добавление связи;
- ручное исправление количества;
- подсветка сомнительных связей;
- экспорт.

---

## 17. Расчёт материалов

### 17.1. Основные материалы

Считать:

- листовой металл;
- профиль;
- пруток;
- труба;
- сотовая панель;
- пластик;
- композит;
- фанера/шпон;
- плёнки;
- кожа/ткань;
- стандартные материалы по справочнику.

### 17.2. Вспомогательные материалы

Считать:

- клей;
- герметик;
- грунт;
- ЛКП;
- растворители;
- обезжириватели;
- абразивы;
- крепёж, если задан как расходник;
- упаковочные материалы;
- технологические материалы.

### 17.3. Припуски и КИМ

Правила должны зависеть от:

```text
material_type
material_grade
process_type
part_geometry
thickness
batch_size
machine/process group
user override
```

Любой расчёт должен хранить:

```json
{
  "net_qty": 1.25,
  "gross_qty": 1.60,
  "unit": "kg",
  "kim": 0.78,
  "allowance": 0.12,
  "waste": 0.23,
  "formula": "gross_qty = net_qty / kim",
  "rule_id": "...",
  "source_facts": ["..."],
  "confidence": 0.84,
  "requires_review": true
}
```

---

## 18. Excel-совместимость

Система должна быть совместима с Excel по двум направлениям.

### 18.1. Импорт шаблонов

Пользователь или администратор загружает Excel-шаблон.

Система должна уметь:

- читать листы;
- видеть заголовки;
- определять области заполнения;
- сохранять стили;
- сохранять формулы, если они не конфликтуют;
- сопоставлять поля системы с ячейками шаблона;
- создавать версию шаблона.

### 18.2. Экспорт

Система формирует:

- ведомость материалов;
- КСИ;
- отчёт;
- сводку по материалам;
- журнал допущений;
- журнал вопросов.

Экспорт должен сохранять оформление шаблона.

### 18.3. Excel-like редактор

В web-интерфейсе нужен табличный режим:

- строки/колонки;
- редактирование ячеек;
- копирование из Excel;
- вставка в Excel;
- фильтры;
- сортировка;
- формулы базового уровня;
- подсветка ячеек, рассчитанных системой;
- подсветка ручных правок;
- журнал изменений.

---

## 19. Админ-панель

Админ-панель должна содержать:

```text
Пользователи и роли
ИИ-провайдеры
Локальные модели Ollama
API-ключи
Лимиты токенов
Мониторинг запросов
Очередь задач
Справочники материалов
Правила КИМ
Правила припусков
Шаблоны Excel
Журнал безопасности
Журнал аудита
Настройки внешнего вида
Настройки резервного копирования
```

API-ключи должны храниться только на сервере в зашифрованном виде.

---

## 20. Информационная безопасность

Обязательные требования:

- HTTPS/TLS в production;
- VPN как дополнительный контур доступа на первом этапе;
- JWT access + refresh tokens;
- RBAC;
- password hashing через Argon2/bcrypt;
- защита от brute force;
- CSRF/XSS защита для web;
- CORS только на разрешённые домены;
- проверка MIME и расширений файлов;
- лимит размера файлов;
- карантин для файлов до проверки;
- запрет выполнения загруженных файлов;
- защита от zip slip;
- защита от path traversal;
- защита от SSRF;
- rate limiting;
- audit log;
- secrets encryption;
- prompt injection protection;
- запрет отправки КД внешнему ИИ без политики доступа;
- маскирование секретов в логах;
- резервное копирование БД и файлов.

---

## 21. Синхронизация и офлайн-режим

Для Windows-приложения и web-клиента:

- все действия пользователя сохраняются локально как pending operations;
- при восстановлении связи операции синхронизируются;
- конфликт решается через ревизии;
- нельзя терять ручные исправления;
- черновики сохраняются автоматически;
- пользователь видит статус синхронизации.

---

## 22. API верхнего уровня

```text
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
GET    /api/v1/users/me

GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}

POST   /api/v1/calculations
GET    /api/v1/calculations/{id}
POST   /api/v1/calculations/{id}/revisions

POST   /api/v1/files/upload
GET    /api/v1/files/{id}

POST   /api/v1/jobs/document-processing
GET    /api/v1/jobs/{id}
GET    /api/v1/jobs/{id}/events
WS     /api/v1/jobs/{id}/stream
POST   /api/v1/jobs/{id}/pause
POST   /api/v1/jobs/{id}/resume
POST   /api/v1/jobs/{id}/cancel

GET    /api/v1/documents/{id}/facts
PATCH  /api/v1/facts/{id}

POST   /api/v1/ksi/build
GET    /api/v1/ksi/{calculation_id}
PATCH  /api/v1/ksi/nodes/{id}

POST   /api/v1/materials/calculate
GET    /api/v1/materials/result/{calculation_id}

POST   /api/v1/templates/excel
POST   /api/v1/exports/excel
GET    /api/v1/exports/{id}/download

GET    /api/v1/admin/ai-providers
POST   /api/v1/admin/ai-providers
GET    /api/v1/admin/token-usage
GET    /api/v1/admin/security-events
```

---

## 23. Этапы разработки в Cursor

### Этап 0. Инициализация репозитория

Результат:

- backend запускается;
- frontend запускается;
- docker compose поднимает Postgres, Redis, MinIO;
- есть `.env.example`;
- есть health-check;
- есть базовые тесты.

Критерии:

```bash
cd backend && pytest
cd frontend && npm run build
docker compose -f infra/docker-compose.yml config
```

### Этап 1. БД, миграции, пользователи, роли

Результат:

- SQLAlchemy модели;
- Alembic миграции;
- регистрация первого администратора;
- login/refresh/me;
- RBAC.

### Этап 2. Проекты, расчёты, ревизии

Результат:

- CRUD проектов;
- CRUD расчётов;
- ревизии;
- audit log.

### Этап 3. Загрузка файлов и объектное хранилище

Результат:

- безопасная загрузка файлов;
- MinIO storage;
- MIME проверка;
- карантин;
- распаковка архивов безопасным способом.

### Этап 4. Очередь задач и ход обработки

Результат:

- worker;
- job model;
- события job;
- WebSocket/SSE поток;
- кнопки pause/resume/cancel.

### Этап 5. Document Intelligence v1

Результат:

- классификация документов;
- text layer extraction;
- OCR для сканов;
- layout/table extraction;
- сохранение фактов с confidence и bbox.

### Этап 6. LLM Router

Результат:

- Ollama provider;
- OpenAI-compatible provider;
- fallback provider;
- structured JSON outputs;
- журнал токенов;
- админ-настройки моделей.

### Этап 7. КСИ

Результат:

- assembly linker;
- KSI tree;
- ручное исправление связей;
- пересчёт входимости;
- экспорт КСИ.

### Этап 8. Материалы и технология

Результат:

- справочники материалов;
- правила КИМ;
- правила припусков;
- основные материалы;
- вспомогательные материалы;
- объяснение расчёта.

### Этап 9. Excel editor/templates/export

Результат:

- загрузка Excel-шаблонов;
- mapping полей;
- Excel-like таблица;
- экспорт с сохранением оформления.

### Этап 10. Админ-панель и мониторинг

Результат:

- пользователи;
- роли;
- провайдеры ИИ;
- токены;
- очереди;
- безопасность;
- справочники.

### Этап 11. Windows-приложение

Результат:

- Tauri shell;
- подключение к серверу;
- local cache;
- sync status;
- сборка `.exe`/installer.

### Этап 12. Hardening и production

Результат:

- security checklist;
- backup/restore;
- logging;
- error monitoring;
- load tests;
- документация установки.

---

## 24. Минимальный MVP, который Cursor должен собрать первым

Не пытаться сразу собрать всю систему. Первый рабочий MVP должен включать:

```text
Auth + роли
Проекты
Расчёты
Загрузка PDF/PNG/JPG/DOCX/XLSX
Сохранение файлов
Очередь обработки
Прогресс обработки
OCR/text extraction
Таблица извлечённых фактов
Ручная корректировка фактов
Простое КСИ дерево
Справочник материалов
Расчёт материалов по правилам
Excel экспорт
Админка для пользователей и ИИ-провайдеров
```

---

## 25. Критерии готовности промышленной версии

Система считается готовой к опытной эксплуатации, если:

- 10+ реальных комплектов КД загружаются и проходят обработку;
- технолог может исправить любые данные до расчёта;
- КСИ строится и редактируется;
- материалы считаются с объяснением формул;
- Excel выгружается по шаблону;
- все действия сохраняются;
- роли работают;
- админ видит расход токенов;
- локальная модель Ollama работает как fallback;
- внешний API-провайдер подключается из админки;
- при пропадании провайдера задача не теряется;
- frontend показывает ход обработки;
- Windows-приложение подключается к серверу;
- есть backup/restore;
- есть журнал безопасности;
- есть документация установки и восстановления.

---

## 26. Главный промпт для Cursor

Скопируй в Cursor файл `prompts/CURSOR_MASTER_PROMPT.md` и работай по нему. Cursor должен выполнять разработку строго по этапам, каждый этап завершать тестами, коммитоподобным отчётом и списком готовности.
