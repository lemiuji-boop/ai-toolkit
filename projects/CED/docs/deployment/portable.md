# Portable EXE (Windows)

Актуальная инструкция: **[windows.md](./windows.md)**.

Кратко:

- `build\windows\build-all.ps1` — сборка **CED-Server** + **CED-Client**
- Сервер: `KdCatalogServer.exe`, `KdCatalogWorker.exe`, `KdCatalog.Server.exe`
- Клиент: `KdCatalog.exe` → API `http://<server>:8000`
- Конфиг: `%APPDATA%\KdCatalog\config.json`
