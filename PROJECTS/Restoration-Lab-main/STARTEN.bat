@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Start
set "LOG=%~dp0START_DIAGNOSE.log"
set "APPLOG=%LOCALAPPDATA%\Restoration Lab\Logs\app.log"
echo === Restoration Lab START === > "%LOG%"
echo [START] %DATE% %TIME% >> "%LOG%"
call "%~dp0PYTHON_STABLE.bat" >> "%LOG%" 2>&1
if errorlevel 1 (echo [FEHLER] Python-Umgebung nicht bereit, siehe Log. & goto end)
"%RL_PY%" ENV_CHECK.py --deps >> "%LOG%" 2>&1
if not errorlevel 1 goto launch
echo [CHECK] Pakete fehlen oder sind defekt. Details im Log.
choice /C JN /M "Pakete aus requirements.txt nur in .venv-gui installieren"
if errorlevel 2 goto end
"%RL_PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
"%RL_PY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (echo [FEHLER] Installation fehlgeschlagen. & goto end)
"%RL_PY%" ENV_CHECK.py --deps >> "%LOG%" 2>&1
if errorlevel 1 (echo [FEHLER] Pakete weiterhin defekt. & goto end)
:launch
echo [START] Restoration Lab wird gestartet ...
"%RL_PY%" windows_entry.py
set "RESULT=%ERRORLEVEL%"
echo [ERGEBNIS] Rueckgabecode %RESULT% >> "%LOG%"
if not "%RESULT%"=="0" (
  echo [FEHLER] Programm mit Code %RESULT% beendet.
  if exist "%APPLOG%" (echo --- app.log, letzte Zeilen --- & powershell -NoProfile -Command "Get-Content -LiteralPath $env:APPLOG -Tail 25")
)
:end
echo.
echo ===== START_DIAGNOSE.log =====
type "%LOG%"
echo.
echo Bei Problemen bitte START_DIAGNOSE.log und app.log schicken.
pause
exit /b 0
