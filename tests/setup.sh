#!/usr/bin/env bash
# Тестларни ишга тушириш учун бир марталик тайёргарлик.
# Ишлатиш:  bash tests/setup.sh
set -e
cd "$(dirname "$0")"

echo "1/3  Python кутубхоналари…"
pip install -q --break-system-packages playwright pypdf openpyxl 2>/dev/null \
  || pip install -q playwright pypdf openpyxl

echo "2/3  Chromium браузери…"
python3 -m playwright install chromium

echo "3/3  JS кутубхоналари (интернетсиз ишлаши учун локал нусха)…"
npm install --silent --no-save --prefix . \
  xlsx@0.18.5 pdf-lib@1.17.1 pdfjs-dist@3.11.174 \
  html2canvas@1.4.1 jspdf@2.5.1 pako@2.1.0 qrcode-generator@1.4.4 \
  || echo "  (npm ўтмади — тестлар CDN'дан олишга уринади)"

echo
echo "Тайёр. Ишга тушириш:  bash tests/run_all.sh"
