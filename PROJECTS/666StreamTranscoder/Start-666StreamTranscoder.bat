@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher (py) was not found.
  echo Install Python 3.10+ and try again.
  pause
  exit /b 1
)
py -3 RadioStreamer.py
if errorlevel 1 (
  echo.
  echo 666StreamTranscoder stopped with an error.
  pause
)
endlocal
