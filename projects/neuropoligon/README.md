# Нейрополигон

Кроссплатформенное обучающее приложение (Kotlin Multiplatform + Compose): токены, эмбеддинги, температура, RAG, агенты — интерактивные песочницы и офлайн-трек «Основы».

## Требования

- JDK 17+
- Android SDK 24+ (для APK)
- Node.js не обязателен для Android/Desktop

## Сборка

```bash
./gradlew :androidApp:assembleDebug      # APK
./gradlew :desktopApp:run                # Desktop
./gradlew :webApp:wasmJsBrowserDevelopmentRun  # Web (Wasm)
./gradlew :shared:desktopTest            # Unit-тесты domain
```

## Запуск

### Android

Установите `androidApp/build/outputs/apk/debug/androidApp-debug.apk` или запустите из Android Studio, открыв корень репозитория.

### Desktop

```bash
./gradlew :desktopApp:run
```

### Web

```bash
./gradlew :webApp:wasmJsBrowserDevelopmentRun
```

Ключи API на Web хранятся в `sessionStorage` (см. предупреждение в настройках). **DeepSeek** в браузере недоступен (CORS); для Anthropic добавлен заголовок direct-browser-access.

## API-ключи

Настройки → выберите провайдера → введите ключ → «Сохранить». Ключи **не** вшиты в приложение. Локальный **Ollama**: провайдер `Local`, URL по умолчанию `http://localhost:11434/v1`.

## Треки

| ID | Название | Ключ |
|----|----------|------|
| foundations | Основы | нет |
| local_ai | Локальные ИИ | нет |
| model_picker | Выбор модели | нет |
| finetuning | Дообучение | нет |
| builder | Сборка | да |

## Supabase Auth (опционально)

Гостевой режим по умолчанию — весь офлайн-контент доступен без аккаунта.

Для облачной синхронизации задайте в `local.properties` (не коммитьте):

```properties
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

Текущая сборка использует локальную сессию (MVP); подключение Supabase SDK — см. `SupabaseAuthService`.

Прогресс при входе: merge по `block_id` (локальные записи сохраняются).

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Нет треков | Проверьте `shared/src/commonMain/composeResources/files/*.json` |
| AI не отвечает | Проверьте ключ, баланс, сеть; на Web — не DeepSeek |
| Прогресс не сохранился (Web) | Wasm использует in-memory до перезагрузки вкладки |
| iOS не собирается на Linux | Собирайте на macOS, см. `iosApp/README.md` |

## Структура

- `shared/` — domain, data, UI, foundations
- `content/` — дубликат JSON (источник: composeResources)
- `androidApp/`, `desktopApp/`, `webApp/` — оболочки

См. `.cursorrules` и `docs/PROGRESS.md`.
