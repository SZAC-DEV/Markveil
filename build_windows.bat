@echo off
setlocal
cd /d "%~dp0"
title PhotoGuard - Compilacao Windows
where py >nul 2>nul || goto :no_python
py -3 -m pip install -e ".[attack]" pyinstaller || goto :error
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name PhotoGuard --paths src launcher.py || goto :error
echo.
echo Executavel criado em dist\PhotoGuard.exe
pause
exit /b 0
:no_python
echo Python nao encontrado. Instale Python 3.10+.
:error
echo.
echo Falha na compilacao. Veja o erro acima.
pause
exit /b 1
