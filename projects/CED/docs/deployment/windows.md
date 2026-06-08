# CED на Windows: сборка EXE и запуск

## Состав дистрибутива

| Пакет | Содержимое | Кому |
|-------|------------|------|
| **CED-Server** | `KdCatalogServer.exe` (API), `KdCatalogWorker.exe` (Celery), `KdCatalog.Server.exe` (GUI), `www/` (веб), скрипты | Сервер в сети |
| **CED-Client** | `KdCatalog.exe` (WinForms) | Рабочие места |

Внешние службы (не входят в EXE, ставятся отдельно):

- **PostgreSQL 15+** — база данных
- **Redis 7+** — очередь Celery
- **Ollama** (опционально) — локальный ИИ на сервере
- Сетевая папка **UNC** — корень каталога PDF (`CATALOG_ROOT`)

---

## Требования для сборки (ПК разработчика)

### Серверный пакет

- Windows 10/11 или Windows Server 2019+
- [Python 3.11 x64](https://www.python.org/downloads/) — «Add to PATH»
- [Node.js 20+](https://nodejs.org/) — для веб-интерфейса в `www/`
- PowerShell 5.1+

### Клиентский пакет

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)

---

## Сборка

Откройте **PowerShell** в корне репозитория:

```powershell
cd C:\Projects\CED
Set-ExecutionPolicy -Scope Process Bypass
.\build\windows\build-all.ps1
```

Отдельно:

```powershell
.\build\windows\build-server.ps1    # dist\CED-Server\
.\build\windows\build-client.ps1    # dist\CED-Client\KdCatalog.exe
.\build\windows\build-server-ui.ps1 # dist\CED-Server-UI\KdCatalog.Server.exe
```

Без веб-UI (только API):

```powershell
.\build\windows\build-server.ps1 -SkipWeb
```

Результат:

```
dist/
  CED-Server/          # API + worker + bat + www
  CED-Client/          # KdCatalog.exe
  CED-Server-UI/       # KdCatalog.Server.exe (скопировать в CED-Server)
```

> PyInstaller собирается **только на Windows**. На Linux используйте CI (GitHub Actions) или VM.

---

## Установка на сервере

### 1. PostgreSQL

1. Установите PostgreSQL 15 с [официального установщика](https://www.postgresql.org/download/windows/).
2. Создайте БД и пользователя:

```sql
CREATE USER ced WITH PASSWORD 'ced_change_me';
CREATE DATABASE ced OWNER ced;
```

### 2. Redis

- Установите [Redis для Windows](https://github.com/microsoftarchive/redis/releases) **или** Memurai, **или** Redis в WSL2/Docker.
- По умолчанию: `127.0.0.1:6379`.

### 3. Каталог UNC

1. Создайте share, например `\\FILESRV\KDCatalog`.
2. Внутри: папки `_INBOX`, `catalog`, права **Изменение** для учётной записи службы CED.

### 4. Развёртывание CED-Server

1. Скопируйте `dist\CED-Server` на сервер, например `C:\CED\`.
2. Скопируйте `KdCatalog.Server.exe` из `CED-Server-UI` в ту же папку.
3. Настройте окружение:

```bat
cd C:\CED
copy .env.example .env
notepad .env
```

Обязательно в `.env`:

- `DATABASE_URL` / `SYNC_DATABASE_URL` — PostgreSQL
- `REDIS_URL` — Redis (нужен для Celery и лимита входа)
- `CATALOG_ROOT=\\FILESRV\KDCatalog` — UNC каталога
- `JWT_SECRET_KEY` / `JWT_REFRESH_SECRET_KEY` — уникальные строки
- `MAX_UPLOAD_BYTES` — лимит загрузки (по умолчанию 100 МБ)
- `LOGIN_RATE_LIMIT_ATTEMPTS` / `LOGIN_RATE_LIMIT_WINDOW_SECONDS` — защита от перебора пароля

Первичная настройка (PowerShell в папке сервера):

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install-server.ps1
```

4. Запуск:

**Миграции БД отдельно (опционально):**

```bat
migrate.bat
```

**Вариант A — скрипт (консоли API + worker):**

```bat
start-server.bat
```

**Вариант B — GUI сервера:**

```bat
KdCatalog.Server.exe
```

При первом запуске укажите UNC каталога. GUI поднимет `KdCatalogServer.exe` и `KdCatalogWorker.exe` из той же папки.

5. Проверка:

```bat
health-check.bat
```

или откройте `http://localhost:8000/docs` — Swagger.

### 5. Веб-интерфейс (опционально)

Папка `www/` — статика Vue. Варианты:

- **IIS** — сайт с корнем `www`, reverse proxy `/api` → `http://127.0.0.1:8000`
- **nginx для Windows** — шаблон `nginx-windows.conf.example` в папке CED-Server (порт 8080, прокси `/api`)
- Пользователи могут работать только через **KdCatalog.exe** без браузера

Вход в веб: `admin` / `admin` — при первом входе система потребует смену пароля (`/auth/change-password`).

### 6. ИИ-агент (опционально)

На сервере с GPU/CPU:

```bat
ollama serve
ollama pull qwen2.5-coder
```

В `.env`: `AI_AGENT_BASE_URL=http://127.0.0.1:11434` (если используете обёртку) или поднимите `ai_agent` через Docker на `8001`.

---

## Установка на клиентских ПК

1. Скопируйте `dist\CED-Client` на ПК (или установщик Inno Setup — см. ниже).
2. Запустите `KdCatalog.exe`.
3. Мастер первого запуска:
   - **Режим:** `client`
   - **Адрес API:** `http://192.168.1.10:8000` (IP/имя **сервера CED**, порт 8000)
4. Вход: `admin` / `admin` — при первом входе обязательна смена пароля (как в веб-клиенте).

Конфиг: `%APPDATA%\KdCatalog\config.json`

---

## Схема сети

```
[Клиенты: KdCatalog.exe] ----HTTP:8000----> [Сервер: KdCatalogServer.exe]
                                                    |
                    +-------------------------------+----------------+
                    |                               |                |
              PostgreSQL                         Redis            UNC каталог
                                                                  (_INBOX, catalog)
```

Откройте в брандмауэре Windows на сервере **TCP 8000** для подсети пользователей.

---

## Остановка служб

```bat
stop-server.bat
```

Или закройте окна «CED API» / «CED Worker» / `KdCatalog.Server.exe`.

---

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| API не стартует | Проверьте PostgreSQL, `.env`, лог в консоли `KdCatalogServer.exe` |
| Worker не обрабатывает | Redis запущен? `REDIS_URL` верный? |
| INBOX не разбирается | `CATALOG_ROOT` доступен на запись, `ENABLE_INBOX_WATCHER=true` |
| Клиент не подключается | Пинг сервера, `http://IP:8000/health`, брандмауэр |
| Нет миграций БД | `migrate.bat` или первый запуск `KdCatalogServer.exe` (alembic upgrade head) |
| 403 после входа | Смените пароль: веб `/change-password` или `POST /auth/change-password` |
| Слишком большой файл | `MAX_UPLOAD_BYTES` в `.env` (байты, по умолчанию 104857600) |

---

## Inno Setup (установщик MSI/EXE)

Шаблон: создайте `desktop_client/KdCatalog.Installer/setup.iss` и укажите:

- `Source: "..\..\dist\CED-Client\*"` — файлы клиента
- Ярлык на рабочий стол → `KdCatalog.exe`

Сборка: [Inno Setup 6](https://jrsoftware.org/isinfo.php) → Compile.

---

## CI (опционально)

Пример шага GitHub Actions: `runs-on: windows-latest`, вызов `build-all.ps1`, артефакты `dist/CED-Server`, `dist/CED-Client`.
