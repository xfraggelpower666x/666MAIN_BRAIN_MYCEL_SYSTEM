@echo off
setlocal
cd /d "%~dp0"
title 666TDI DAEMON R1.1
echo ============================================
echo    666TDI DAEMON R1.1 - LOCAL CONTROL CENTER
echo ============================================
echo Browser: http://127.0.0.1:8766
echo Fuer Abbruch: STRG+C
echo.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m engine.daemon_cli --port 8766
  goto :end
)
where python >nul 2>nul
if not errorlevel 1 (
  python -m engine.daemon_cli --port 8766
  goto :end
)
echo Python 3.10+ nicht gefunden. Keine automatische Installation.
pause
:end
endlocal
