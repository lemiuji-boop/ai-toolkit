# Ubuntu: Ollama + SSH для туннеля с Windows-шлюза

## Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
ollama pull qwen2.5-coder
```

Ограничить прослушивание localhost (в `/etc/systemd/system/ollama.service` или env):

```ini
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
curl http://127.0.0.1:11434/api/tags
```

## Пользователь только для туннеля

```bash
sudo useradd -m -s /bin/bash cedtunnel
sudo mkdir -p /home/cedtunnel/.ssh
sudo chmod 700 /home/cedtunnel/.ssh
# Вставьте содержимое tunnel\id_ed25519.pub с Windows:
sudo nano /home/cedtunnel/.ssh/authorized_keys
sudo chmod 600 /home/cedtunnel/.ssh/authorized_keys
sudo chown -R cedtunnel:cedtunnel /home/cedtunnel/.ssh
```

Опционально в `authorized_keys`:

```
restrict,port-forwarding,permitopen=127.0.0.1:11434 ssh-ed25519 AAAA...
```

## frp (если SSH закрыт)

На Ubuntu (`frps.toml`):

```toml
bindPort = 7000
auth.token = "change-me-frp-token"
```

```bash
./frps -c frps.toml
```

На Windows — `tunnel\frpc.ini` из `frpc.ini.example`, `TUNNEL_MODE=frpc`.

Секция на Ubuntu (`frpc` на той же машине что Ollama):

```toml
serverAddr = "127.0.0.1"
serverPort = 7000

[[proxies]]
name = "ollama_stcp"
type = "stcp"
secretKey = "change-me-stcp-secret"
localIP = "127.0.0.1"
localPort = 11434
```

## Проверка с Windows

После `start-tunnel.bat`:

```bat
health-check-ollama.bat
```
