@echo off
setlocal
cd /d "%~dp0"
title Markveil Studio
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv || goto :error
)
".venv\Scripts\python.exe" -m pip install -e ".[desktop]" || goto :error
".venv\Scripts\python.exe" -m markveil.gui
if errorlevel 1 goto :error
exit /b 0
:error
echo Falha ao iniciar Markveil. Verifique Python 3.10+ e a conexao de internet.
pause
exit /b 1
