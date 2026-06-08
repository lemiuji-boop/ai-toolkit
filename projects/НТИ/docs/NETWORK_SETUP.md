# Сеть: Wi‑Fi и интернет

## Почему работало только по USB

`adb reverse` пробрасывает `127.0.0.1:8010` на ПК. По **Wi‑Fi** телефон обращается к **IP ПК** (например `192.168.248.202:8010`).

На Linux по умолчанию **файрвол блокирует входящие** на порт 8010 — с телефона получается таймаут.

## Wi‑Fi (та же сеть)

1. Запустите сервер:
   ```bash
   cd backend && ./scripts/run_dev.sh
   ```

2. Откройте порт (один раз на ПК):
   ```bash
   sudo ufw allow 8010/tcp
   sudo ufw reload
   ```
   Или: `sudo ./scripts/open_firewall.sh`

3. Проверка и сборка APK:
   ```bash
   ./scripts/setup_wifi.sh
   cd ../android && ./gradlew assembleProdDebug
   adb install -r app/build/outputs/apk/prod/debug/app-prod-debug.apk
   ```

4. Телефон и ПК в **одной Wi‑Fi**, USB не нужен.

## Интернет (вне офиса / без проброса портов)

### Вариант A: Cloudflare Tunnel (быстро для теста)

```bash
# терминал 1
cd backend && ./scripts/run_dev.sh

# терминал 2
./scripts/tunnel_public.sh
# появится https://xxxx.trycloudflare.com
```

В `android/local.properties`:
```properties
ntiApiBaseUrl=https://xxxx.trycloudflare.com/
```

Пересоберите и установите APK. Работает из любой сети (мобильный интернет).

### Вариант B: Сервер в облаке (production)

VPS + домен + HTTPS (nginx + Let's Encrypt). В сборке:
```properties
ntiApiBaseUrl=https://api.ваш-домен.ru/
```

### Вариант C: Проброс на роутере

Пробросить внешний порт 8010 → IP ПК:8010, в APK указать `http://ВАШ_БЕЛЫЙ_IP:8010/` (лучше HTTPS через reverse proxy).

## USB (только разработка)

```bash
adb reverse tcp:8010 tcp:8010
# ntiApiBaseUrl=http://127.0.0.1:8010/
```

Не используйте для обычной работы — только отладка.
