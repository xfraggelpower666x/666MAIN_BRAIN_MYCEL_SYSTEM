@echo off
setlocal
cd /d "%~dp0"

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist ".venv-build" rmdir /s /q ".venv-build"

echo Build-Verzeichnisse wurden entfernt. Quelldateien bleiben erhalten.
pause
