@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Audio-Reparatur
rem FFmpeg wird NICHT benoetigt: MP3 wird ueber soundfile/libsndfile gelesen, Wiedergabe ueber PortAudio (sounddevice).
call "%~dp0PYTHON_STABLE.bat"
if errorlevel 1 (pause & exit /b 2)
"%RL_PY%" ENV_CHECK.py --deps
set "DEPS=%ERRORLEVEL%"
"%RL_PY%" ENV_CHECK.py --audio
set "AUD=%ERRORLEVEL%"
if "%DEPS%"=="0" if "%AUD%"=="0" (echo [PASS] Audio-Laufzeit in Ordnung. & pause & exit /b 0)
if not "%DEPS%"=="0" (
  echo [OFFEN] soundfile / sounddevice neu installieren? Benoetigt Internet.
  choice /C JN /M "Nur in .venv-gui neu installieren"
  if errorlevel 2 (pause & exit /b 3)
  "%RL_PY%" -m pip install --upgrade --force-reinstall "soundfile>=0.13.1,<1" "sounddevice>=0.4.6,<1"
  if errorlevel 1 (echo [FEHLER] Installation fehlgeschlagen. & pause & exit /b 4)
  "%RL_PY%" ENV_CHECK.py --deps
  if errorlevel 1 (pause & exit /b 5)
)
if not "%AUD%"=="0" echo [HINWEIS] Kein Ausgabegeraet: Kopfhoerer/Lautsprecher in den Windows-Soundeinstellungen aktivieren.
pause
exit /b 0
