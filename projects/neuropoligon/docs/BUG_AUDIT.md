# Багаудит Нейрополигон

| Проблема | Причина | Исправление |
|----------|---------|-------------|
| GlobalScope/runBlocking в prod | Требование `.cursorrules` | Не используются; auth init без runBlocking |
| Офлайн без ключей | Трек foundations | `requiresApiKey: false`, офлайн sandboxes |
| AI без ключа | Нет ключа в storage | `AiComparison.degradationMessage`, демо для function/agent |
| DeepSeek на Web | CORS | `AiCapabilities.availableOnWeb = false`, фильтр в Settings |
| Anthropic Web | Блокировка браузера | Заголовок `anthropic-dangerous-direct-browser-access` |
| Парсинг JSON | Невалидные поля | `ignoreUnknownKeys`, defaults в моделях |
| Прогресс Android/Desktop | SQLDelight | Файл БД на диске |
| Прогресс Web | Нет JDBC на Wasm | `InMemoryProgressRepository` |
| Ключи в git | Секреты | `.gitignore` `.env`; grep чистый |
| Гостевой режим | Auth optional | Обучение без входа |
| Смена уровня | StateFlow в Settings | `levelFlow` + `ContentEngine.combine` |
| Глоссарий scroll | AlertDialog | Не меняет scroll state урока |
| URL каталога | resources.json | Официальные ссылки из ТЗ |

Проверка ключей: `git grep -i apikey` — ожидается пусто (только документация).

Проверка URL: вручную / скрипт — все `officialUrl` из `resources.json` ведут на домены из ТЗ.
