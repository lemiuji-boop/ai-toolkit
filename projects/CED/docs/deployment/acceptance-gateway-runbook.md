# Прогон приёмки: Windows-шлюз + Ubuntu Ollama

Используйте вместе с [acceptance-gateway-checklist.md](./acceptance-gateway-checklist.md).

## День 1 — Ubuntu

1. [ubuntu-tunnel-setup.md](./ubuntu-tunnel-setup.md) — Ollama + `cedtunnel`.
2. Проверка: `curl http://127.0.0.1:11434/api/tags`.

## День 2 — Сборка (Windows с SDK)

```powershell
git clone ...
cd CED
.\build\windows\build-all.ps1
```

Скопировать `dist\CED-Server` на шлюз в LAN (флешка / share).

## День 3 — Шлюз без админа

1. Распаковать в `%USERPROFILE%\CED-Server`.
2. `runtime\` — бинарники по README.
3. `init-runtime.bat`
4. `setup-tunnel.bat` + ключ на Ubuntu.
5. `copy env.gateway.example .env` → JWT, `CATALOG_ROOT`.
6. `start-server.bat`
7. Чеклист разделы B, C, H.

## День 4 — Пользователи

1. `CED-Client\KdCatalog.exe` + `config.client.example.json`.
2. INBOX тест (раздел E).
3. Браузер `:8080` (раздел G).

## День 5 — Отказоустойчивость

1. `stop-tunnel.bat` → анализ без LLM (H2).
2. `start-tunnel.bat` → LLM снова (H3).
3. `stop-server.bat` / `start-server.bat` (I).

Зафиксируйте результаты в чеклисте (дата, исполнитель, IP шлюза).
