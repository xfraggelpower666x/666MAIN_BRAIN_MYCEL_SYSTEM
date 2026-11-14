@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0PORTABLE_VERIFY.ps1"
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (echo [PASS] Ordnerdateien und Audio-Tools geprueft.) else (echo [FAIL] Der Portable-Ordner ist noch nicht vollstaendig.)
pause
exit /b %RESULT%
