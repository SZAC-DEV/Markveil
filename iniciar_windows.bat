@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% -m pip install -e .
if errorlevel 1 goto error
%PY% -m markveil.gui
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo Houve um erro. Copie a mensagem acima para diagnostico.
pause
exit /b 1
