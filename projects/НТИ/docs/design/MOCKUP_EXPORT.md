# Экспорт макетов для подписания

## Вариант 1 — Android Studio (рекомендуется)

1. Откройте проект `android/` в Android Studio.
2. Файл: `app/src/main/java/ru/nti/sbor/ui/preview/DesignMockupPreviews.kt`
3. В панели **Split / Design** выберите превью группы **signoff**:
   - `01 Главный — светлая 360`
   - `02 Главный — тёмная 360`
   - `03 Форма записи — светлая`
   - `04 Настройки — светлая`
   - `05 Главный — шрифт 200%`
4. ПКМ на превью → **Save as Image** (PNG) → сохраните в `docs/design/exports/`.
5. Вложите PNG к `DESIGN_SIGNOFF.md` или распечатайте для подписи.

## Вариант 2 — Живое приложение

```bash
cd android && ./gradlew :app:installDevDebug
```

Установите APK на телефон из матрицы ТЗ (раздел 5) и пройдите чек-лист в `DESIGN_SIGNOFF.md`.

## Вариант 3 — Статичные примеры

Готовые иллюстрации-ориентиры (сгенерированные по ТЗ):

- [mockup_01_home_light.png](mockup_01_home_light.png)
- [mockup_02_home_dark.png](mockup_02_home_dark.png)
- [mockup_03_record_form.png](mockup_03_record_form.png)
- [mockup_04_settings.png](mockup_04_settings.png)

Цвет акцента: `#1C4F80` (стальной синий НТИ).
