@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666 ChatBackup PC Tool - Automatischer Python-Start

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode Run -ForceSource
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" pause
exit /b %EXITCODE%
