#!/bin/zsh
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[desktop]'
python -m markveil.gui
