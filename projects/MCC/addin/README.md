# Надстройка МАТНОРМ-XL (Office.js)

Статическая Office-надстройка для Excel. Данные КД идут **напрямую Excel ↔ on-prem бэкенд**
в локальной сети (LAN). Cloudflare tunnel **не используется** по умолчанию.

## Быстрый старт (Ubuntu-хост, LAN)

```bash
# Бэкенд HTTPS + RAG + admin + упаковка add-in (без cloudflared)
./scripts/start-matnorm-stack.sh

# Только экспорт КД
./scripts/export-and-analyze.sh
```

После запуска:
- `addin/lan-host.txt` — IP сервера в LAN (например `192.168.248.202`)
- `addin/config.json` — `backendUrl` = `https://<IP>:8123`
- Готовый архив: `addin/matnorm-addin.zip`

Проверка на сервере:

```bash
LAN=$(cat addin/lan-host.txt)
curl -k "https://${LAN}:8123/health"
curl -k "https://${LAN}:8123/api/addin/catalog" | head -c 300
```

Firewall (если `ufw` активен): `sudo ufw allow 8123/tcp`

## Установка на Windows **без прав администратора** (LAN)

Схема: Ubuntu-сервер по WiFi, Windows ПК по Ethernet — **одна подсеть** `192.168.x.x`.

### 1. Узнать IP сервера

На Ubuntu после `./scripts/start-matnorm-stack.sh` в выводе будет строка `Server IP:`  
или: `cat addin/lan-host.txt` → например `192.168.248.202`.

**LAN URL:** `https://192.168.248.202:8123` (подставьте свой IP).

### 2. Принять self-signed сертификат (один раз в браузере)

На Windows ПК откройте **Edge**:

```
https://192.168.248.202:8123/addin/taskpane.html
```

Нажмите **«Дополнительно»** → **«Перейти на сайт…»** (самоподписанный сертификат LAN).  
Без этого шага Excel/WebView2 может отказать в загрузке надстройки.

### 3. Скопировать и установить надстройку

1. Скопируйте `addin/matnorm-addin.zip` на Windows (USB, общая папка, RDP).
2. Распакуйте в `C:\Users\<имя>\matnorm-addin\`.
3. Excel → **Вставка** → **Мои надстройки** → **Загрузить мою надстройку**.
4. Выберите **`manifest.xml`** (не zip и не папку).
5. На ленте **Главная** → группа **МАТНОРМ** → **МАТНОРМ-XL**.

### 4. Антивирус

Если антивирус блокирует подключение (раньше — Cloudflare tunnel):

- Добавьте **исключение для IP сервера** `192.168.x.x` в настройках антивируса (профиль пользователя, без прав админа — если доступно).
- Убедитесь, что ноутбук (WiFi) и ПК (Ethernet) в одной подсети.

### 5. Проверка

1. Откройте панель **МАТНОРМ-XL** → **«Проверить и сохранить»** — зелёный индикатор.
2. **«Обновить каталог»** — список отчётов и заданий.

---

## Опционально: Cloudflare tunnel (вне LAN)

Только для временной отладки: `USE_TUNNEL=1 ./scripts/start-matnorm-stack.sh`  
URL сохраняется в `.tunnel-url` и `addin/config.json`.

## Установка на Windows **без прав администратора** (sideload)

Office-надстройка не требует установки в систему — достаточно загрузить manifest.

### Шаг 1. Скопировать надстройку на Windows

Вариант A — архив (рекомендуется):

1. С Ubuntu-хоста скопируйте `addin/matnorm-addin.zip` на Windows (USB, сеть, RDP).
2. Распакуйте в любую папку, например `C:\Users\<имя>\matnorm-addin\`.

Вариант B — папка:

1. Скопируйте целиком `addin/dist/` на Windows.

### Шаг 2. Запустить стек на Ubuntu

```bash
cd projects/MCC
./scripts/start-matnorm-stack.sh
```

Убедитесь, что tunnel активен. Актуальный URL:

```bash
cat .tunnel-url
# или
cat addin/config.json
```

Пример: `https://thirty-define-position-commonwealth.trycloudflare.com`

### Шаг 3. Загрузить надстройку в Excel

> **Критично:** в диалоге «Загрузить мою надстройку» указывайте файл **`manifest.xml`**,  
> **не** `matnorm-addin.zip` и **не** папку. Excel не принимает zip как manifest.

1. Откройте **Excel** (Desktop, Microsoft 365 или Excel в браузере).
2. **Вставка** → **Мои надстройки** → **Загрузить мою надстройку**  
   (в англ. Excel: **Insert** → **My Add-ins** → **Upload My Add-in**).
3. В проводнике выберите **`manifest.xml`**:
   - из распакованного архива: `C:\Users\<имя>\matnorm-addin\manifest.xml`
   - или скопированная папка `dist\manifest.xml` с Ubuntu-хоста.
4. Подтвердите доверие, если Excel спросит.
5. Кнопка **МАТНОРМ-XL** появится на вкладке **Главная** (группа **МАТНОРМ**).

### Шаг 4. Проверить подключение

1. Откройте панель **МАТНОРМ-XL** (появится на ленте или в «Мои надстройки»).
2. Адрес сервиса подставится из `config.json` (HTTPS tunnel).
3. Нажмите **«Проверить и сохранить»** — индикатор должен стать зелёным («Сервер доступен»).
4. Нажмите **«Обновить каталог»** — появятся группы: отчёты, задания, эталонные xlsx.

### Шаг 5. Выгрузка расчёта из каталога

- В каталоге выберите задание → **«Скачать»** (файл JSON) или **«В панель»** / **«В лист»**.
- В блоке **«Запрос / чат»** введите: `выгрузить расчёт` или `каталог`.
- Команда `задание f661d067` загружает расчёт по префиксу хеша.

> Mixed content: tunnel даёт HTTPS → бэкенд и API на том же origin (`/addin/`, `/api/`).
> Не используйте `http://127.0.0.1` в Excel на Windows, если manifest указывает HTTPS tunnel.

## Устранение неполадок

### Ошибка сертификата / Certificate

Excel Desktop **не доверяет** самоподписанным сертификатам и **не принимает** `http://127.0.0.1` /
`https://localhost` в manifest на Windows. Quick tunnel Cloudflare (`*.trycloudflare.com`) выдаёт
**публичный HTTPS** с цепочкой Google Trust Services — это рекомендуемый путь **без прав администратора**.

#### Почему Excel ругается на сертификат

| Причина | Как распознать | Что делать |
|--------|----------------|------------|
| **A. Неверный manifest** | В XML есть `localhost`, `127.0.0.1` или старый `*.trycloudflare.com` | Только `addin/dist/manifest.xml` после `./scripts/package-addin.sh` |
| **B. Самоподписанный локальный HTTPS** | Manifest ссылается на `https://localhost:8123` | Пересобрать с tunnel URL (опция A), убрать локальные URL |
| **C. Tunnel перезапущен, manifest старый** | Браузер открывает новый URL, в manifest — другой хост | `./scripts/start-tunnel.sh` → `./scripts/package-addin.sh` → заново sideload |
| **D. Корпоративный антивирус / SSL inspection** | Браузер тоже предупреждает; сертификат не Cloudflare/Google | Исключение для `*.trycloudflare.com` или отключить HTTPS-сканирование для этого домена |
| **E. Tunnel мёртв** | `curl` к URL из manifest → timeout / 502 на статику | Перезапустить tunnel и пересобрать add-in |

Проверка сертификата tunnel **на Ubuntu-хосте** (должно быть `Verification: OK`):

```bash
TUNNEL=$(cat .tunnel-url)
HOST="${TUNNEL#https://}"
echo | openssl s_client -connect "${HOST}:443" -servername "$HOST" 2>&1 | grep -E 'subject=|issuer=|Verification:'
curl -s -o /dev/null -w "taskpane: %{http_code}\n" "$TUNNEL/addin/taskpane.html"
```

Ожидаемо: `subject=CN = trycloudflare.com`, `issuer=... Google Trust Services`, taskpane **200**.

#### Пошагово на Windows (без прав администратора)

1. **Проверьте tunnel в браузере** (Edge или Chrome): откройте URL из `manifest.xml`, например  
   `https://….trycloudflare.com/addin/taskpane.html`  
   - Страница должна открыться. Если браузер предупреждает о сертификате — сначала устраните это (часто антивирус); Excel повторит ту же проверку.
   - **Один раз** откройте корневой tunnel URL в Edge до sideload — так WebView2 «прогревает» доверие к origin (см. `SIDELOAD.txt` в zip).

2. **Убедитесь, что manifest актуален** (на Ubuntu):
   ```bash
   ./scripts/start-tunnel.sh      # или ./scripts/start-matnorm-stack.sh
   ./scripts/package-addin.sh
   cat .tunnel-url
   ```
   Скопируйте **новый** `matnorm-addin.zip` на Windows, распакуйте, используйте **новый** `manifest.xml`.

3. **Не используйте** `addin/manifest.xml` из репозитория — там шаблон с `localhost` / `127.0.0.1`.

4. **Повторный sideload в Excel:**  
   Вставка → Мои надстройки → Загрузить мою надстройку → выберите свежий `manifest.xml`.

5. **Антивирус / корпоративный прокси:** если подменяется SSL, добавьте исключение для `*.trycloudflare.com` или временно отключите HTTPS-инспекцию для этого домена (без прав админа — через настройки личного профиля антивируса, если доступны).

6. **Сетевой каталог** (если sideload блокируется политикой, но есть доступ к общей папке):  
   Файл → Параметры → Центр управления безопасностью → Параметры центра → **Надёжные каталоги надстроек** →  
   укажите UNC-путь к папке с `manifest.xml` (например `\\server\share\matnorm-addin\`).  
   Права администратора **не нужны**, если пользователь может писать в эту папку или админ один раз положил manifest.

#### Варианты решения (сводка)

| Вариант | Когда | Действие |
|--------|-------|----------|
| **A (лучший)** | Обычная установка | Только `*.trycloudflare.com` в manifest → `package-addin.sh` → sideload |
| **B** | Был локальный self-signed HTTPS | Убрать localhost из manifest, перейти на tunnel (A) |
| **C** | Политика Excel блокирует upload | Trusted Add-in Catalogs на сетевой share |
| **D** | Только dev, cert всё ещё не доверен | IE/Edge «Надёжные узлы» — **может потребовать админа**, крайний случай |
| **E** | Quick tunnel нестабилен / блокируется | Named Cloudflare Tunnel + свой домен с валидным cert — см. `scripts/start-tunnel.sh` (`CLOUDFLARE_TUNNEL_TOKEN`) |

Если после перезапуска tunnel сертификат или статика не отвечают:

```bash
./scripts/start-tunnel.sh
./scripts/package-addin.sh
# скопировать zip на Windows и загрузить manifest заново
```

### Excel не воспринимает файл (zip / «не является надстройкой»)

| Симптом | Причина | Решение |
|--------|---------|---------|
| «Файл не является допустимой надстройкой» при выборе `.zip` | Excel ожидает **XML**, не архив | Распакуйте zip → выберите **`manifest.xml`** |
| То же при выборе папки | Нужен конкретный файл manifest | Укажите полный путь к `manifest.xml` |
| Manifest отклонён, иконки недоступны | Tunnel выключен или URL устарел | `./scripts/start-tunnel.sh` → `./scripts/package-addin.sh` |
| Использован `addin/manifest.xml` из репозитория | Шаблон с `localhost` / `127.0.0.1` | Берите **`addin/dist/manifest.xml`** после `package-addin.sh` |
| Надстройка не на ленте | Старая версия manifest без VersionOverrides | Пересоберите zip, загрузите manifest заново |
| Desktop Excel без «Загрузить мою надстройку» | Ограничение политики / старая сборка | **Сетевой каталог:** положите `manifest.xml` в общую папку → Файл → Параметры → Центр управления безопасностью → **Надёжные каталоги надстроек** |

Проверка manifest перед установкой (на Ubuntu):

```bash
./scripts/package-addin.sh
xmllint --noout addin/dist/manifest.xml
TUNNEL=$(cat .tunnel-url)
curl -s -o /dev/null -w "taskpane: %{http_code}\n" "$TUNNEL/addin/taskpane.html"
curl -s -o /dev/null -w "icon-32: %{http_code}\n" "$TUNNEL/addin/assets/icon-32.png"
```

Все URL в manifest должны отвечать **200** при активном tunnel.

### Прочие проблемы

| Симптом | Причина | Решение |
|--------|---------|---------|
| Красный индикатор, «Нет связи» | Tunnel не запущен или URL устарел | Перезапустите `./scripts/start-tunnel.sh`, обновите `config.json`, пересоберите zip |
| Mixed content blocked | HTTP API при HTTPS taskpane | Используйте tunnel URL (HTTPS), не localhost |
| CORS error в консоли F12 | Origin не в белом списке | В `.env` бэкенда: `CORS_ORIGIN_REGEX=^https://[a-z0-9-]+\.trycloudflare\.com$` (уже по умолчанию) |
| Excel не показывает надстройку | Блокировка Центра управления безопасностью | Файл → Параметры → Центр управления безопасностью → Параметры центра → **Надёжные каталоги надстроек** → добавьте папку с manifest |
| «Сервис не отвечает» | Бэкенд не слушает :8123 | `curl http://127.0.0.1:8123/health` на Ubuntu |
| Пустой каталог | Нет экспорта | Запустите `./scripts/export-and-analyze.sh` |

### Проверка с Ubuntu (без Excel)

```bash
TUNNEL=$(cat .tunnel-url)
curl -s "$TUNNEL/health"
curl -s "$TUNNEL/api/addin/catalog" | head -c 500
curl -s -X POST "$TUNNEL/api/addin/fetch-job" \
  -H 'Content-Type: application/json' \
  -d '{"job_hash":"f661d06700be"}' | head -c 300
```

### Чеклист на Windows (после sideload)

- [ ] Зелёный индикатор связи в панели
- [ ] Каталог показывает отчёты и задания
- [ ] «Скачать» на `report_summary.json` сохраняет файл
- [ ] «В лист» по заданию заполняет ведомость на листе
- [ ] Команда `выгрузить расчёт` в чате загружает последнее задание

## Альтернатива: сетевой каталог

Положите `manifest.xml` в общую папку; пользователь один раз добавляет путь в  
Excel → Параметры → Центр управления безопасностью → Каталоги надстроек.

## Сборка dist / zip

```bash
./scripts/start-tunnel.sh    # URL → .tunnel-url и addin/config.json
./scripts/package-addin.sh
# → addin/dist/manifest.xml  — для sideload (выбрать этот файл в Excel)
# → addin/matnorm-addin.zip  — для копирования на Windows (распаковать, затем manifest.xml)
```

Скрипт читает tunnel из `.tunnel-url` (приоритет) или `addin/config.json`, подставляет HTTPS во все URL,
синхронизирует статику в `addin/` для раздачи через `/addin/` на бэкенде.

## API надстройки (бэкенд)

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Проверка связи |
| GET | `/api/addin/catalog` | Каталог выгрузок (без обозначений) |
| POST | `/api/addin/fetch-job` | Расчёт по `job_hash` |
| POST | `/api/addin/export` | Метаданные + URL скачивания |
| GET | `/api/addin/download?path=…` | Скачивание файла |

## Деплой на Vercel (опционально)

```bash
npm i -g vercel
cd addin
vercel --prod
```

После деплоя подставьте URL в `manifest.xml` и добавьте в `CORS_ORIGINS` бэкенда.

## Конфигурация

| Файл | Назначение |
|---|---|
| `config.json` | `backendUrl`, `tunnelUrl` — обновляется `start-tunnel.sh` |
| `taskpane.js` | Читает `config.json`, хранит override в `localStorage` |

Адрес бэкенда по умолчанию не хардкодится в коде — только в `config.json` / manifest.
