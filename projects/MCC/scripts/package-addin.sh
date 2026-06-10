#!/usr/bin/env bash
# Сборка addin/dist/ и matnorm-addin.zip для sideload без прав администратора.
# Excel принимает только manifest.xml (не .zip) в «Загрузить мою надстройку».
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADDIN="$ROOT/addin"
DIST="$ADDIN/dist"
ZIP="$ADDIN/matnorm-addin.zip"
TUNNEL_FILE="$ROOT/.tunnel-url"
LAN_HOST_FILE="$ADDIN/lan-host.txt"
BACKEND_PORT="${BACKEND_PORT:-8123}"

# Иконки 32/64/80 (минимальные PNG через Python)
gen_icons() {
  python3 - "$ADDIN/icons" <<'PY'
import struct, zlib, sys
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

def png(size: int, rgb: tuple[int, int, int]) -> bytes:
    w, h = size, size
    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            # простой крест в центре
            if abs(x - w // 2) < 2 or abs(y - h // 2) < 2 or (x < 4 and y < 4):
                raw += bytes(rgb)
            else:
                raw += bytes((0x1F, 0x38, 0x64))
    comp = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")

for name, size in [("icon-32.png", 32), ("icon-64.png", 64), ("icon-80.png", 80)]:
    (out / name).write_bytes(png(size, (255, 255, 255)))
print(f"→ icons: {out}")
PY
}

resolve_base_url() {
  local placeholder="https://REPLACE-WITH-LAN-URL"
  if [[ -n "${LAN_BASE_URL:-}" ]]; then
    echo "${LAN_BASE_URL%/}"
    return 0
  fi
  if [[ -f "$LAN_HOST_FILE" ]]; then
    local ip
    ip="$(tr -d '[:space:]' <"$LAN_HOST_FILE")"
    if [[ -n "$ip" ]]; then
      echo "https://${ip}:${BACKEND_PORT}"
      return 0
    fi
  fi
  if [[ -f "$TUNNEL_FILE" ]]; then
    local url
    url="$(tr -d '[:space:]' <"$TUNNEL_FILE")"
    if [[ -n "$url" ]]; then
      echo "$url"
      return 0
    fi
  fi
  if [[ -f "$ADDIN/config.json" ]]; then
    python3 -c "import json; c=json.load(open('$ADDIN/config.json')); print(c.get('backendUrl') or c.get('tunnelUrl','$placeholder'))"
    return 0
  fi
  echo "$placeholder"
}

gen_icons
mkdir -p "$DIST/assets" "$ADDIN/assets"

BASE_URL="$(resolve_base_url)"
ADDIN_BASE="${BASE_URL%/}/addin"
BACKEND_URL="${BASE_URL%/}"

cp "$ADDIN/taskpane.html" "$ADDIN/taskpane.css" "$ADDIN/taskpane.js" "$DIST/"
echo "{\"backendUrl\":\"$BACKEND_URL\",\"addinUrl\":\"$ADDIN_BASE\",\"tunnelUrl\":\"$BACKEND_URL\",\"lanMode\":true}" >"$DIST/config.json"

cp "$ADDIN/icons/"*.png "$DIST/assets/"
cp "$ADDIN/icons/"*.png "$ADDIN/assets/"

# config.json и иконки — для LAN (backend отдаёт /addin/ из addin/, не dist/)
cp "$DIST/config.json" "$ADDIN/config.json"

# manifest с HTTPS LAN URL
python3 - "$ADDIN_BASE" "$BACKEND_URL" "$DIST/manifest.xml" <<'PY'
import sys
from pathlib import Path

addin_base, backend, dest = sys.argv[1:4]
taskpane = f"{addin_base.rstrip('/')}/taskpane.html"
icon32 = f"{addin_base.rstrip('/')}/assets/icon-32.png"
icon64 = f"{addin_base.rstrip('/')}/assets/icon-64.png"
icon80 = f"{addin_base.rstrip('/')}/assets/icon-80.png"
manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:bt="http://schemas.microsoft.com/office/officeappbasictypes/1.0"
           xsi:type="TaskPaneApp">
  <Id>a1b2c3d4-e5f6-7890-abcd-ef1234567890</Id>
  <Version>0.1.0</Version>
  <ProviderName>МАТНОРМ</ProviderName>
  <DefaultLocale>ru-RU</DefaultLocale>
  <DisplayName DefaultValue="МАТНОРМ-XL"/>
  <Description DefaultValue="Распознавание КД и 3D, расчёт норм, нормоконтроль в Excel."/>
  <IconUrl DefaultValue="{icon32}"/>
  <HighResolutionIconUrl DefaultValue="{icon64}"/>
  <SupportUrl DefaultValue="{backend}"/>
  <Hosts><Host Name="Workbook"/></Hosts>
  <Requirements>
    <Sets DefaultMinVersion="1.1"><Set Name="ExcelApi" MinVersion="1.7"/></Sets>
  </Requirements>
  <DefaultSettings>
    <SourceLocation DefaultValue="{taskpane}"/>
  </DefaultSettings>
  <Permissions>ReadWriteDocument</Permissions>
  <AppDomains>
    <AppDomain>{backend.rstrip('/')}</AppDomain>
  </AppDomains>
  <VersionOverrides xmlns="http://schemas.microsoft.com/office/taskpaneappversionoverrides" xsi:type="VersionOverridesV1_0">
    <Requirements>
      <bt:Sets DefaultMinVersion="1.1">
        <bt:Set Name="ExcelApi" MinVersion="1.7"/>
      </bt:Sets>
    </Requirements>
    <Hosts>
      <Host xsi:type="Workbook">
        <DesktopFormFactor>
          <GetStarted>
            <Title resid="GetStarted.Title"/>
            <Description resid="GetStarted.Description"/>
            <LearnMoreUrl resid="GetStarted.LearnMoreUrl"/>
          </GetStarted>
          <FunctionFile resid="Commands.Url"/>
          <ExtensionPoint xsi:type="PrimaryCommandSurface">
            <OfficeTab id="TabHome">
              <Group id="CommandsGroup">
                <Label resid="CommandsGroup.Label"/>
                <Icon>
                  <bt:Image size="16" resid="Icon.16x16"/>
                  <bt:Image size="32" resid="Icon.32x32"/>
                  <bt:Image size="80" resid="Icon.80x80"/>
                </Icon>
                <Control xsi:type="Button" id="TaskpaneButton">
                  <Label resid="TaskpaneButton.Label"/>
                  <Supertip>
                    <Title resid="TaskpaneButton.Label"/>
                    <Description resid="TaskpaneButton.Tooltip"/>
                  </Supertip>
                  <Icon>
                    <bt:Image size="16" resid="Icon.16x16"/>
                    <bt:Image size="32" resid="Icon.32x32"/>
                    <bt:Image size="80" resid="Icon.80x80"/>
                  </Icon>
                  <Action xsi:type="ShowTaskpane">
                    <TaskpaneId>MatnormTaskpane</TaskpaneId>
                    <SourceLocation resid="Taskpane.Url"/>
                  </Action>
                </Control>
              </Group>
            </OfficeTab>
          </ExtensionPoint>
        </DesktopFormFactor>
      </Host>
    </Hosts>
    <Resources>
      <bt:Images>
        <bt:Image id="Icon.16x16" DefaultValue="{icon32}"/>
        <bt:Image id="Icon.32x32" DefaultValue="{icon32}"/>
        <bt:Image id="Icon.80x80" DefaultValue="{icon80}"/>
      </bt:Images>
      <bt:Urls>
        <bt:Url id="GetStarted.LearnMoreUrl" DefaultValue="{backend}"/>
        <bt:Url id="Commands.Url" DefaultValue="{taskpane}"/>
        <bt:Url id="Taskpane.Url" DefaultValue="{taskpane}"/>
      </bt:Urls>
      <bt:ShortStrings>
        <bt:String id="GetStarted.Title" DefaultValue="МАТНОРМ-XL"/>
        <bt:String id="CommandsGroup.Label" DefaultValue="МАТНОРМ"/>
        <bt:String id="TaskpaneButton.Label" DefaultValue="МАТНОРМ-XL"/>
      </bt:ShortStrings>
      <bt:LongStrings>
        <bt:String id="GetStarted.Description" DefaultValue="Распознавание КД и расчёт норм в Excel."/>
        <bt:String id="TaskpaneButton.Tooltip" DefaultValue="Открыть панель МАТНОРМ-XL"/>
      </bt:LongStrings>
    </Resources>
  </VersionOverrides>
</OfficeApp>
"""
Path(dest).write_text(manifest, encoding="utf-8")
print(f"→ manifest: {taskpane}")
PY

# Инструкция для Windows (кладётся в zip)
cat >"$DIST/SIDELOAD.txt" <<EOF
МАТНОРМ-XL — установка в Excel (Windows, локальная сеть)

ВАЖНО: в диалоге «Загрузить мою надстройку» выберите файл manifest.xml,
       НЕ matnorm-addin.zip и не папку.

Перед sideload (принять self-signed сертификат один раз):
  Откройте в Edge:
  $BASE_URL/addin/taskpane.html
  Нажмите «Дополнительно» → «Перейти на сайт…» (самоподписанный сертификат LAN).

Шаги:
1. Распакуйте matnorm-addin.zip в C:\\Users\\<имя>\\matnorm-addin\\
2. Ubuntu: ./scripts/start-matnorm-stack.sh (без Cloudflare tunnel)
3. Откройте LAN URL в Edge (см. выше)
4. Excel → Вставка → Мои надстройки → Загрузить мою надстройку
5. Укажите: ...\\matnorm-addin\\manifest.xml
6. На ленте «Главная» → «МАТНОРМ-XL»

Антивирус: добавьте исключение для IP сервера $BACKEND_URL (не блокировать LAN).
WiFi ноутбук и Ethernet ПК должны быть в одной подсети (192.168.x.x).

LAN URL в manifest: $BASE_URL
EOF

rm -f "$DIST"/icon-*.png

rm -f "$ZIP"
(
  cd "$DIST"
  zip -qr "$ZIP" manifest.xml taskpane.html taskpane.css taskpane.js config.json assets SIDELOAD.txt
)

if command -v xmllint >/dev/null 2>&1; then
  xmllint --noout "$DIST/manifest.xml"
  echo "✓ xmllint: manifest.xml OK"
fi

if [[ "$BASE_URL" != *REPLACE-WITH-LAN* ]]; then
  for path in /addin/taskpane.html /addin/assets/icon-32.png /addin/assets/icon-64.png; do
    code="$(curl -sk -o /dev/null -w '%{http_code}' "${BASE_URL}${path}" || echo "000")"
    if [[ "$code" != "200" ]]; then
      echo "⚠ ${BASE_URL}${path} → HTTP $code (запустите ./scripts/start-matnorm-stack.sh)" >&2
    else
      echo "✓ ${BASE_URL}${path} → 200"
    fi
  done
else
  echo "⚠ LAN URL не задан — запустите ./scripts/start-matnorm-stack.sh" >&2
fi

echo "✓ dist: $DIST"
echo "✓ zip:  $ZIP (manifest.xml в корне архива)"
echo "  Для Excel выберите manifest.xml из распакованного zip или $DIST/manifest.xml"
