@echo off
setlocal
cd /d "%~dp0"
call ENSURE_BUILD_TOOLS.bat runtime
if errorlevel 1 (pause & exit /b 1)
call npm start
if errorlevel 1 pause
