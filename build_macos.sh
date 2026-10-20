#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -e '.[desktop]' pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name Markveil --osx-bundle-identifier org.markveil.studio --add-data "src/markveil/assets:markveil/assets" --collect-all tkinterdnd2 --paths src launcher.py
echo 'App em dist/Markveil.app. Não assinado/notarizado; build deve ser feito no macOS.'
