@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title 666 ChatBackup PC Tool - VerifyHost v1.10.5

if "%~1"=="" (
    powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode VerifyHost
) else (
    powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode VerifyHost -ShareUrl "%~1"
)
set "RC=%ERRORLEVEL%"
if not defined CHATBACKUP_NO_PAUSE pause
exit /b %RC%
