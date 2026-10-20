@echo off
setlocal
cd /d "%~dp0"
title PhotoGuard - Inicializador
where py >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado. Instale Python 3.10 ou superior e marque Add Python to PATH.
  goto :error
)
py -3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ necessario'" 2>nul
if errorlevel 1 (
  echo ERRO: e necessario Python 3.10 ou superior.
  goto :error
)
echo Instalando/verificando dependencias do PhotoGuard...
py -3 -m pip install -e ".[attack]"
if errorlevel 1 goto :error
echo.
echo Abrindo PhotoGuard...
py -3 -m photoguard.gui
if errorlevel 1 goto :error
exit /b 0
:error
echo.
echo Ocorreu um erro. Copie as mensagens acima ou envie uma captura de tela.
pause
exit /b 1
