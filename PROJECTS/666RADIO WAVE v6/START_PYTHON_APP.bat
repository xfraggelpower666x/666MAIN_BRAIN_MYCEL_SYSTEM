@echo off
cd /d "%~dp0"
call ENSURE_PYTHON_HOST_TOOLS.bat runtime
if errorlevel 1 (pause & exit /b 1)
py -3.12 soundwave_666.py
