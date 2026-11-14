@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666SOUNDsDESIGn - Portable EXE Builder
call "%~dp0PYTHON_STABLE.bat"
if errorlevel 1 (pause & exit /b 2)
set "PY=%~dp0.venv_stable\Scripts\python.exe"
"%PY%" SYSTEM_CHECK.py --build-check
if not errorlevel 1 goto build
choice /C JN /M "Fehlende Build-Pakete nur in .venv_stable installieren"
if errorlevel 2 exit /b 3
"%PY%" SYSTEM_CHECK.py --install --build
if errorlevel 1 (echo [FEHLER] Installation fehlgeschlagen. & pause & exit /b 4)
"%PY%" SYSTEM_CHECK.py --build-check
if errorlevel 1 (echo [FEHLER] Abhaengigkeiten defekt. & pause & exit /b 5)
:build
"%PY%" SYSTEM_CHECK.py --build
if errorlevel 1 (echo [FEHLER] EXE-Build fehlgeschlagen. & pause & exit /b 6)
echo [PASS] dist\L.Y.V.R.A._MP3_MANAGER\L.Y.V.R.A._MP3_MANAGER.exe
echo [INFO] Immer den gesamten Ordner dist\L.Y.V.R.A._MP3_MANAGER kopieren.
pause
