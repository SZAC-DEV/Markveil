@echo off
setlocal
cd /d "%~dp0"
title Markveil Studio
py -3 -m pip install -e ".[desktop]" || goto :error
py -3 -m markveil.gui
if errorlevel 1 goto :error
exit /b 0
:error
echo Falha ao iniciar Markveil.
pause
exit /b 1
