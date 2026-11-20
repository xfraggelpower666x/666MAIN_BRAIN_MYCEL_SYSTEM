@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666SOUNDsDESIGn - Startdiagnose
set "LOG=%~dp0START_DIAGNOSE.log"
echo === 666SOUNDsDESIGn STARTDIAGNOSE === > "%LOG%"
echo [START] %DATE% %TIME% >> "%LOG%"
echo [INFO] Protokoll: "%LOG%"
call "%~dp0PYTHON_STABLE.bat" >> "%LOG%" 2>&1
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
 echo [FEHLER] Stabile Python-Laufzeit nicht bereit. Code %RESULT%
 goto end
)
set "PY=%~dp0.venv_stable\Scripts\python.exe"
"%PY%" SYSTEM_CHECK.py >> "%LOG%" 2>&1
if errorlevel 1 (
 echo [CHECK] Abhaengigkeiten fehlerhaft; Details im Log.
 choice /C JN /M "Nur in .venv_stable fehlende Python-Pakete installieren"
 if errorlevel 2 goto end
 "%PY%" SYSTEM_CHECK.py --install >> "%LOG%" 2>&1
 if errorlevel 1 goto end
 "%PY%" SYSTEM_CHECK.py >> "%LOG%" 2>&1
 if errorlevel 1 goto end
)
echo [START] GUI wird gestartet (Fenster schliesst erst nach Diagnose).
"%PY%" SYSTEM_CHECK.py --launch >> "%LOG%" 2>&1
set "RESULT=%ERRORLEVEL%"
echo [ERGEBNIS] GUI-Rueckgabecode %RESULT% >> "%LOG%"
echo [ERGEBNIS] GUI-Rueckgabecode %RESULT%
:end
echo.
echo ===== DIAGNOSE-AUSGABE =====
type "%LOG%"
echo.
echo Bitte START_DIAGNOSE.log bei weiteren Problemen senden.
pause
exit /b 0
