@echo off
setlocal EnableExtensions
cd /d "%~dp0" || exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0HOST_ABNAHME_WINDOWS.ps1"
set "RC=%errorlevel%"
if not "%RC%"=="0" echo [FEHLER] Windows Host-Diagnose fehlgeschlagen.
if /i not "%~1"=="/nopause" pause
exit /b %RC%
