@echo off
setlocal EnableExtensions DisableDelayedExpansion
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -STA -File "%~dp0STARTEN.ps1" %*
set "RC=%errorlevel%"
if not "%RC%"=="0" if "%~1"=="" pause
exit /b %RC%
