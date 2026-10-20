@echo off
setlocal
cd /d "%~dp0"
title Markveil - Build Windows
py -3 -m pip install -e ".[desktop]" pyinstaller || goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name Markveil --icon src\markveil\assets\markveil.ico --add-data "src\markveil\assets;markveil\assets" --collect-all tkinterdnd2 --paths src launcher.py || goto :error
echo Executavel em dist\Markveil.exe
pause
exit /b 0
:error
echo Erro na compilacao.
pause
exit /b 1
