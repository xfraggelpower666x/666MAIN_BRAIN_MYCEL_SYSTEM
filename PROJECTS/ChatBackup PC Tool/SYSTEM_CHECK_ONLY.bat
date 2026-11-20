@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666 ChatBackup PC Tool - Systempruefung

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode Audit
set "EXITCODE=%ERRORLEVEL%"
echo.
if "%EXITCODE%"=="0" (
    echo VERIFIZIERT: Systempruefung abgeschlossen.
) else (
    echo BLOCKIERT: Systempruefung fehlgeschlagen.
)
echo.
pause
exit /b %EXITCODE%
