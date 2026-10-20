@echo off
setlocal
cd /d "%~dp0"
py -m pip install -e . pyinstaller || goto :error
py -m PyInstaller --noconfirm --clean --onefile --windowed --name PhotoGuard --paths src launcher.py || goto :error
echo.
echo Executavel criado em dist\PhotoGuard.exe
pause
exit /b 0
:error
echo Falha na compilacao. Veja as mensagens acima.
pause
exit /b 1
