@echo off
setlocal
cd /d "%~dp0"
call ENSURE_PYTHON_HOST_TOOLS.bat build
if errorlevel 1 (pause & exit /b 1)
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed --name "SoundwaveStudio666-PythonHost" soundwave_666.py
if errorlevel 1 (echo PYTHON HOST EXE BUILD FAILED & pause & exit /b 1)
echo PYTHON HOST EXE BUILD PASS - see dist\SoundwaveStudio666-PythonHost.exe
pause
