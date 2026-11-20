@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "tools\archive_intelligence_gui.py"
) else (
  python "tools\archive_intelligence_gui.py"
)
if errorlevel 1 pause
