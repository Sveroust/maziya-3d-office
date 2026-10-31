#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================================="
echo "  PT MAZIYA MEDICAL GLOBAL — 3D Interactive Office & CDAKB"
echo "=========================================================="
echo "Membuka tampilan 3D di Safari..."
open -a Safari "http://localhost:8888"

if ! lsof -i :8888 >/dev/null 2>&1; then
  echo "Menjalankan server web lokal..."
  python3 -m http.server 8888
else
  echo "Server lokal port 8888 sudah aktif. Safari berhasil diluncurkan!"
fi
