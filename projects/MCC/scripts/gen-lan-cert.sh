#!/usr/bin/env bash
# Самоподписанный TLS-сертификат для HTTPS Excel add-in в локальной сети.
# Результат: deploy/certs/lan.key, deploy/certs/lan.crt (SAN: LAN IP + hostname).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT_DIR="$ROOT/deploy/certs"
LAN_IP="${1:-$(hostname -I | awk '{print $1}')}"
HOSTNAME="${2:-$(hostname -s 2>/dev/null || echo matnorm)}"
DAYS="${CERT_DAYS:-825}"

if [[ -z "$LAN_IP" ]]; then
  echo "Ошибка: не удалось определить LAN IP (hostname -I)" >&2
  exit 1
fi

mkdir -p "$CERT_DIR"
KEY="$CERT_DIR/lan.key"
CRT="$CERT_DIR/lan.crt"

if [[ -f "$KEY" && -f "$CRT" ]]; then
  # Перегенерировать, если SAN не содержит текущий IP
  if openssl x509 -in "$CRT" -noout -text 2>/dev/null | grep -q "IP Address:${LAN_IP}"; then
    echo "✓ Сертификат уже есть для $LAN_IP: $CRT"
    exit 0
  fi
  echo "→ IP изменился ($LAN_IP), перегенерация сертификата…"
fi

echo "→ Генерация self-signed TLS для $LAN_IP (SAN: IP, $HOSTNAME, localhost)"
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout "$KEY" \
  -out "$CRT" \
  -days "$DAYS" \
  -subj "/CN=${LAN_IP}/O=MATNORM/C=RU" \
  -addext "subjectAltName=IP:${LAN_IP},DNS:${HOSTNAME},DNS:localhost"

chmod 600 "$KEY"
chmod 644 "$CRT"
echo "✓ $KEY"
echo "✓ $CRT"
