# CED: единый сервер на Ubuntu (актуальная схема)

Один сервер в корпоративной инфраструктуре. **Windows-шлюз и SSH-туннель к Ollama не используются.**

| Где | Что |
|-----|-----|
| **Ubuntu-сервер** | Docker: API, Celery, ai-agent, PostgreSQL, Redis, nginx + **Ollama на хосте** |
| **Ubuntu** | OpenVPN → доступ к **UNC/SMB** каталогу КД (mount в `/mnt/ced-catalog`) |
| **ПК Windows** | `KdCatalog.exe` → API `:8000`; браузер → `:80` |

Устаревшие документы (не применять к новым установкам): [windows-gateway-bundle.md](./windows-gateway-bundle.md), [lan-split-ai-tunnel.md](./lan-split-ai-tunnel.md).

---

## Схема

```
  [Windows user] ──HTTP:8000──┐
  [Windows browser] ──:80───┼──► [Ubuntu CED] ──OpenVPN──► [FILES] \\corp\KDCatalog
                              │         │
                              │         └── Ollama 127.0.0.1:11434
                              └── Docker: backend, worker, ai-agent, PG, Redis
```

---

## 1. Ubuntu: базовое ПО

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin socat cifs-utils openvpn
sudo usermod -aG docker "$USER"
# перелогиниться для группы docker

curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder   # или ваша модель
curl http://127.0.0.1:11434/api/tags
```

Ollama только на localhost (рекомендуется):

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
printf '%s\n' '[Service]' 'Environment=OLLAMA_HOST=127.0.0.1:11434' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

---

## 2. OpenVPN и каталог КД

1. Получите у IT профиль OpenVPN (`.ovpn`) для **сервера** CED.
2. Подключение (пример):

```bash
sudo openvpn --config /etc/openvpn/ced-client.ovpn --daemon
```

3. Смонтируйте share (после VPN):

```bash
sudo mkdir -p /mnt/ced-catalog
sudo nano /etc/ced-smb.credentials   # username=... password=... domain=...
sudo chmod 600 /etc/ced-smb.credentials

sudo mount -t cifs //FILESRV/KDCatalog /mnt/ced-catalog \
  -o credentials=/etc/ced-smb.credentials,uid=$(id -u),gid=$(id -g),file_mode=0660,dir_mode=0770
```

Внутри должны быть `_INBOX`, `catalog` (или как в вашей политике).

Автомонтирование: `/etc/fstab` или systemd unit после `openvpn.service`.

---

## 3. Развёртывание CED

```bash
git clone <repo> /opt/ced && cd /opt/ced
cp .env.server.example .env
nano .env   # CED_CATALOG_MOUNT, пароли, JWT, AI ключи
```

Обязательно в `.env`:

```ini
CED_CATALOG_MOUNT=/mnt/ced-catalog
CED_PUBLIC_HOST=192.168.248.202
POSTGRES_PASSWORD=...
JWT_SECRET_KEY=...
AI_AGENT_API_KEY=...
AI_API_KEY=...          # тот же
```

```bash
chmod +x scripts/deploy-ubuntu-server.sh
./scripts/deploy-ubuntu-server.sh
```

Проверки:

```bash
curl -s http://127.0.0.1/api/health
curl -s http://127.0.0.1:8000/health
```

---

## 4. Клиенты Windows (без изменений exe)

Соберите клиент на Windows (или из CI): `dist\CED-Client\KdCatalog.exe`.

Рядом с exe — `config.json`:

```json
{
  "Mode": "client",
  "ServerUrl": "http://192.168.248.202:8000",
  "CatalogUnc": "",
  "Theme": "system",
  "FontSize": "normal"
}
```

`192.168.248.202` — IP/DNS Ubuntu-сервера, **доступный с ПК пользователя** (LAN или VPN).

| Роль | URL |
|------|-----|
| Пользователь / модератор (exe) | `http://<CED_HOST>:8000` |
| Модератор (браузер) | `http://<CED_HOST>/` |
| Вход | `admin` / `admin` → сменить пароль |

Веб собирается **без** `VITE_API_BASE_URL` — запросы идут на `/api` через nginx.

---

## 5. Firewall (Ubuntu)

Разрешить с подсети клиентов:

```bash
sudo ufw allow from 192.168.0.0/16 to any port 80,8000 proto tcp
sudo ufw allow OpenSSH
sudo ufw enable
```

Порт **11434** наружу не открывать.

---

## 6. Обслуживание

```bash
./scripts/deploy-ubuntu-server.sh --skip-web   # перезапуск без пересборки UI
./scripts/deploy-ubuntu-server.sh --down
docker compose -f docker-compose.yml -f docker-compose.server.yml logs -f backend
```

Мост Ollama для Docker: `scripts/ollama-docker-bridge.sh` (запускается скриптом deploy).

---

## Сравнение со старой схемой

| Было | Стало |
|------|--------|
| Windows-шлюз + portable PG/Redis | Не нужен |
| SSH-туннель к Ubuntu для Ollama | Ollama на том же Ubuntu |
| UNC с Windows-шлюза | UNC через OpenVPN только на Ubuntu |
| Два IP (25.x / 248.x) | Один адрес сервера для клиентов |
