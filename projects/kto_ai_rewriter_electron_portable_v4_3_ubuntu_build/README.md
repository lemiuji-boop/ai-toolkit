# KTO AI Editor v4.2 ASCII Fixed

Эта версия исправляет ошибку запуска `.bat/.cmd`, когда CMD выводит сообщения вида:

```text
'is not recognized as an internal or external command'
```

Причина: Windows CMD нестабильно обрабатывает кириллицу в именах и тексте `.bat`-файлов, особенно после распаковки ZIP. В v4.2 все командные файлы и технические имена переведены в ASCII.

## Как правильно распаковать

Распакуйте архив в простой путь без кириллицы и пробелов:

```text
C:\kto_ai_rewriter_electron_portable_v4_2_ascii_fixed
```

Не запускайте файлы прямо из архива ZIP.

## Порядок сборки

1. Запустите:

```text
CHECK_ENV.cmd
```

2. Проверьте запуск без сборки:

```text
RUN_WITHOUT_BUILD.cmd
```

3. Соберите portable EXE:

```text
BUILD_PORTABLE_EXE.cmd
```

Готовый EXE будет в папке:

```text
dist
```

## Ярлык для пользователей

После запуска приложения или сервера выполните:

```text
CREATE_GUEST_SHORTCUT.cmd
```

Будет создан файл:

```text
KTO_AI_Editor_Guest.url
```

Его можно отправить пользователям или положить на общий диск.

## Если сборка упала

Откройте файл:

```text
build-log.txt
```

и пришлите последние 30–40 строк.
