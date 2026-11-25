@echo off
setlocal EnableExtensions
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build\BUILD.ps1" %*
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (echo BUILD FAILED ^(exit %RC%^)) else (echo BUILD STEP COMPLETED)
pause
exit /b %RC%
