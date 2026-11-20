@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title 666 ChatBackup PC Tool - VerifyRuntime v1.10.5

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode VerifyRuntime
set "RC=%ERRORLEVEL%"
if not defined CHATBACKUP_NO_PAUSE pause
exit /b %RC%
