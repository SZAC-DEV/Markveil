#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -e '.[desktop]' pyinstaller
python3 -m PyInstaller --noconfirm --clean --onedir --windowed --name Markveil --add-data "src/markveil/assets:markveil/assets" --collect-all tkinterdnd2 --paths src launcher.py
echo 'Build em dist/Markveil/Markveil (Linux). Execute em um Linux com interface gráfica.'
