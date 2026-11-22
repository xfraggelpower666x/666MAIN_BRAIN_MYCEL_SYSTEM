@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build\BUILD_WINDOWS.ps1" %*
exit /b %errorlevel%
