# Deployment

## Актуальная схема (2026): единый Ubuntu-сервер

**Один сервер** с Docker, Ollama, OpenVPN к корпоративным папкам. Клиенты — Windows (`KdCatalog.exe`) и браузер.

→ **[ubuntu-single-server.md](./ubuntu-single-server.md)** — полная инструкция

```bash
cp .env.server.example .env
# настроить CED_CATALOG_MOUNT, секреты
./scripts/deploy-ubuntu-server.sh
```

---

## Локальная разработка (Ubuntu / Linux)

```bash
cp .env.example .env
mkdir -p data/catalog
echo "CED_CATALOG_MOUNT=$(pwd)/data/catalog" >> .env
./scripts/start-dev-ubuntu.sh
```

Веб: http://localhost/ · API: http://localhost/api/health

---

## Устаревшие схемы (архив)

Не использовать для новых установок:

| Документ | Было |
|----------|------|
| [windows-gateway-bundle.md](./windows-gateway-bundle.md) | Portable Windows-шлюз |
| [lan-split-ai-tunnel.md](./lan-split-ai-tunnel.md) | ИИ на Ubuntu + туннель с Windows |
| [ubuntu-tunnel-setup.md](./ubuntu-tunnel-setup.md) | SSH только для туннеля |
| [acceptance-gateway-checklist.md](./acceptance-gateway-checklist.md) | Приёмка шлюза |

Общие сведения по LAN-клиентам: [lan-enterprise.md](./lan-enterprise.md) (обновлён под Ubuntu-сервер).

Сборка WinForms: [windows.md](./windows.md) — только **CED-Client**, серверный EXE-шлюз опционален для legacy.
