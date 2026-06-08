# CED в локальной сети предприятия (без прав администратора на ПК пользователей)

> **Актуальная установка:** один **Ubuntu-сервер** (Docker + Ollama + OpenVPN к файловому каталогу).
> → **[ubuntu-single-server.md](./ubuntu-single-server.md)**

> Устарело: Windows-шлюз + туннель к Ollama — [lan-split-ai-tunnel.md](./lan-split-ai-tunnel.md), [windows-gateway-bundle.md](./windows-gateway-bundle.md).

## Роли машин

| Узел | ОС | Что крутится | Кто настраивает |
|------|-----|--------------|-----------------|
| **CED-SRV** | **Ubuntu** | Docker: API, Celery, ai-agent, PG, Redis, nginx; Ollama на хосте | IT |
| **FILES** | NAS / Windows | UNC/SMB каталог КД | IT |
| **CED-SRV** | Ubuntu | OpenVPN-клиент → mount `CED_CATALOG_MOUNT` | IT |
| **ПК пользователя** | Windows | `KdCatalog.exe` → `http://CED-SRV:8000` | без админа |
| **ПК модератора** | Windows | браузер `http://CED-SRV/` | без админа |

## Схема сети

```
                    Локальная сеть предприятия (192.168.x.x / 10.x.x.x)
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                                                                             │
  │   [ПК user]     [ПК moderator]              [CED-SRV]                       │
  │   KdCatalog.exe  браузер :80                  Docker или CED-Server EXE       │
  │        │              │                            │                          │
  │        │  HTTP :8000  │  HTTP :80 (/api)          │                          │
  │        └──────────────┼────────────────────────────┤                          │
  │                       │                            │                          │
  │                       │                     ┌──────┴──────┐                   │
  │                       │                     │ PostgreSQL  │                   │
  │                       │                     │ Redis       │                   │
  │                       │                     └──────┬──────┘                   │
  │                       │                            │ SMB / CIFS              │
  │                       │                            ▼                          │
  │                       │                     [FILES] \\FILESRV\KDCatalog       │
  │                       │                            ▲                          │
  │                       │                     [ai-agent + Ollama в LAN]          │
  └─────────────────────────────────────────────────────────────────────────────┘

  Ollama на том же CED-SRV (localhost), см. ubuntu-single-server.md.
```

## Важно про порты

| Клиент | URL | Почему |
|--------|-----|--------|
| **WinForms `KdCatalog.exe`** | `http://CED-SRV:8000` | Клиент ходит в API **напрямую**, без префикса `/api` |
| **Браузер (веб)** | `http://CED-SRV/` или `http://CED-SRV:80` | Nginx отдаёт `www/` и проксирует `/api` → backend |

На **CED-SRV** в брандмауэре откройте для подсети предприятия:

- **TCP 8000** — desktop-клиенты
- **TCP 80** — веб (модераторы, админ)
- **не открывайте 8001** наружу — только `ai-agent` ↔ `backend` внутри LAN/ Docker

---

## Часть 1. Сервер CED (вы можете поднять на Ubuntu)

### 1.1 Docker на CED-SRV (рекомендуется)

```bash
cd /opt/CED
cp .env.example .env
# отредактировать .env — см. ниже
cd web_client && npm install && npm run build && cd ..
docker compose up -d --build
```

В `docker-compose.yml` для сценария с desktop-клиентами **опубликуйте API**:

```yaml
  backend:
    ports:
      - "8000:8000"
```

В `.env` для продакшена в LAN:

```env
APP_ENV=production
DEBUG=false

# если PostgreSQL на том же хосте — в compose уже postgres:5432
DATABASE_URL=postgresql+asyncpg://ced:СЕКРЕТ@postgres:5432/ced
SYNC_DATABASE_URL=postgresql://ced:СЕКРЕТ@postgres:5432/ced
REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=длинная-случайная-строка
JWT_REFRESH_SECRET_KEY=другая-длинная-строка

AI_AGENT_BASE_URL=http://192.168.1.30:8001
AI_AGENT_API_KEY=общий-секрет-backend-ai

# CORS для браузеров по IP/имени сервера (JSON-массив)
CORS_ORIGINS=["http://192.168.1.10","http://ced-srv","http://ced-srv.local"]
```

### 1.2 Подключение каталога КД (UNC → Linux)

На **FILES** создайте шару, например `\\FILESRV\KDCatalog`, папки `_INBOX` и `catalog`.

На **CED-SRV** (нужны права **IT**, не пользователя):

```bash
sudo apt install cifs-utils
sudo mkdir -p /mnt/kdcatalog
sudo nano /etc/fstab
# //FILESRV/KDCatalog /mnt/kdcatalog cifs credentials=/root/.smbced,uid=1000,file_mode=0660,dir_mode=0770 0 0
sudo mount -a
```

В `docker-compose.yml` примонтируйте каталог вместо volume `catalog_data`:

```yaml
  backend:
    volumes:
      - file_storage:/data/storage
      - /mnt/kdcatalog:/data/catalog
```

Учётная запись в `credentials` — **служба CED** с правом **Изменение** на шару.

### 1.3 Альтернатива: сервер на Windows

Сборка на Windows-машине IT: `build\windows\build-all.ps1` → папка `CED-Server` на `C:\CED\`.

- `.env`: `CATALOG_ROOT=\\FILESRV\KDCatalog`
- Запуск: `install-server.ps1` → `start-server.bat`
- API слушает `0.0.0.0:8000` — откройте в брандмауэре Windows Server.

---

## Часть 2. ИИ

- **Ollama в той же LAN**, что и шлюз: провайдер в веб-UI → `http://192.168.x.x:11434`.
- **Ollama на внешней Ubuntu без LAN**: см. **[lan-split-ai-tunnel.md](./lan-split-ai-tunnel.md)** — `ai-agent` на шлюзе, LLM по SSH/VPN-туннелю.

---

## Часть 3. ПК пользователей и модераторов (без админа)

### 3.1 Распространение клиента

1. IT **один раз** собирает `dist\CED-Client\KdCatalog.exe` (на Windows с .NET 8 SDK).
2. Кладёт папку на общий ресурс, например `\\FILESRV\Apps\CED\`.
3. Пользователь копирует к себе в `C:\Users\Иван\Apps\CED\` **или** запускает по ярлыку с сети (если политика разрешает).

Установки в `Program Files` **не требуется**.

### 3.2 Первый запуск клиента

1. Запустить `KdCatalog.exe`.
2. Мастер:
   - **Режим:** `client`
   - **Адрес сервера:** `http://192.168.1.10:8000` (IP или DNS-имя **CED-SRV**)
   - **UNC каталога:** оставить пустым (каталог обслуживает сервер, не клиент)
3. Вход `admin` / `admin` только для проверки; рабочие учётки выдаёт администратор.

Конфиг: `%APPDATA%\KdCatalog\config.json` — пишется **без прав администратора**.

### 3.3 Преднастройка (если IT может раздать login-script)

Файл `%APPDATA%\KdCatalog\config.json`:

```json
{
  "Mode": "client",
  "ServerUrl": "http://ced-srv.company.local:8000",
  "CatalogUnc": "",
  "Theme": "system",
  "FontSize": "normal"
}
```

### 3.4 Модераторы через браузер

- URL: `http://ced-srv.company.local/` (порт 80)
- Роли `moderator` / `admin` в вебе: пользователи, загрузка, мониторинг, настройки
- После первого входа — обязательная смена пароля

---

## Часть 4. Учётные записи и роли

| Роль | Desktop | Web |
|------|---------|-----|
| user | каталог, поиск, карточка | то же |
| moderator | + провайдеры (если в клиенте) | пользователи, загрузка, мониторинг |
| admin | полный доступ | + настройки, ИИ-провайдеры |

Создание пользователей: веб → **Администрирование → Пользователи** (под учёткой admin).

---

## Часть 5. Чеклист IT (один раз)

- [ ] CED-SRV: Docker или Windows EXE, порты **80** и **8000** в LAN
- [ ] PostgreSQL, Redis доступны с CED-SRV
- [ ] UNC `\\FILESRV\KDCatalog` и права службы CED
- [ ] `CORS_ORIGINS` и сильные `JWT_*` в `.env`
- [ ] AI-SRV: Ollama, при необходимости `ai-agent`
- [ ] DNS или hosts: имя `ced-srv` → IP сервера
- [ ] Раздача `KdCatalog.exe` + ярлык / предзаполненный `config.json`
- [ ] Проверка: `curl http://CED-SRV:8000/health` и вход в браузере

## Часть 6. Проверка с рабочего ПК (без админа)

```text
ping ced-srv
curl http://ced-srv:8000/health
```

Запуск `KdCatalog.exe` → вход → каталог открывается.

---

## Что вы делаете на Ubuntu vs что на Windows

| Задача | Где |
|--------|-----|
| Поднять API, БД, веб, worker | **Ubuntu CED-SRV** (`docker compose`) |
| Собрать `KdCatalog.exe` | **Windows** (VM или ПК IT), один раз |
| Работа пользователей | **Windows** в LAN, без админа |
| Файлы КД | **FILES** (UNC), сервер CED монтирует шару |
| ИИ | **AI-SRV** в LAN |

Связанные документы: [windows.md](./windows.md), [README.md](./README.md).
