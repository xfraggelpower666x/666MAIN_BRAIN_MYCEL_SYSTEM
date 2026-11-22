@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666 ChatBackup PC Tool - EIN EXE Build

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap\bootstrap.ps1" -Mode Build
if errorlevel 1 goto :failed

if not exist ".venv-build\Scripts\python.exe" goto :failed
".venv-build\Scripts\python.exe" -m PyInstaller --noconfirm --clean "666_CHATBACKUP_PC_TOOL.spec"
if errorlevel 1 goto :failed

if not exist "dist\666_CHATBACKUP_PC_TOOL.exe" goto :failed

echo.
echo ============================================================
echo VERIFIZIERT: EXE wurde erzeugt:
echo %CD%\dist\666_CHATBACKUP_PC_TOOL.exe
echo ============================================================
echo.
pause
exit /b 0

:failed
echo.
echo BUILD FEHLGESCHLAGEN.
echo Die bestehende Projektstruktur wurde nicht destruktiv veraendert.
echo Pruefe die Bootstrap- und Build-Meldungen oberhalb.
echo.
pause
exit /b 1
