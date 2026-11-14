@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Tests
call "%~dp0PYTHON_STABLE.bat"
if errorlevel 1 (pause & exit /b 2)
"%RL_PY%" ENV_CHECK.py --deps
if errorlevel 1 (echo [FEHLER] Zuerst STARTEN.bat ausfuehren und Pakete installieren. & pause & exit /b 3)
echo [TEST] 47 Tests, dauert ca. 1 Minute. Ausgabe auch in TEST.log
"%RL_PY%" -m unittest discover -v > TEST.log 2>&1
set "RESULT=%ERRORLEVEL%"
powershell -NoProfile -Command "Get-Content -LiteralPath 'TEST.log' -Tail 15"
if "%RESULT%"=="0" (echo [PASS] Alle Tests bestanden.) else (echo [FAIL] Tests fehlgeschlagen, Details in TEST.log.)
pause
exit /b %RESULT%
