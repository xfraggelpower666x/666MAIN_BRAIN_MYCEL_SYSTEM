@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666 ChatBackup PC Tool - Automatischer Systemstart

where powershell.exe >nul 2>&1
if errorlevel 1 goto :no_powershell

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode Run
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo AUTOMATISCHER SYSTEMSTART BLOCKIERT.
    echo Die genaue Ursache steht in der angezeigten Logdatei.
    echo.
    pause
)
exit /b %EXITCODE%

:no_powershell
echo.
echo BLOCKIERT: Windows PowerShell wurde nicht gefunden.
echo Windows 10 oder Windows 11 enthaelt PowerShell normalerweise bereits.
echo.
pause
exit /b 1
