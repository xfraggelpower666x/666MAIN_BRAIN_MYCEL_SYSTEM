@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Portable EXE Builder
rem Der Build (Build-Windows.ps1) benoetigt Python 3.13 x64 mit Tcl/Tk und dem py-Launcher.
where py >nul 2>nul
if errorlevel 1 (echo [FEHLT] py-Launcher nicht gefunden. Python 3.13 x64 von python.org installieren. & pause & exit /b 2)
py -3.13 -c "import sys,tkinter; sys.exit(0 if sys.maxsize>2**32 else 1)" >nul 2>nul
if errorlevel 1 (echo [FEHLT] Python 3.13 x64 mit Tcl/Tk nicht gefunden. & pause & exit /b 3)
echo [BUILD] Erstellt .venv-windows, installiert Pakete, fuehrt Tests und Selbsttest aus (mehrere Minuten, Internet noetig).
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-Windows.ps1"
if errorlevel 1 (echo [FEHLER] Build fehlgeschlagen. & pause & exit /b 4)
echo [PASS] dist\Restoration Lab\Restoration Lab.exe
echo [PASS] Restoration-Lab-3.0-Windows-x64.zip
echo [INFO] Immer den GESAMTEN Ordner "dist\Restoration Lab" kopieren, nicht nur die EXE.
echo [INFO] Danach PORTABLE_VERIFY.bat ausfuehren.
pause
exit /b 0
