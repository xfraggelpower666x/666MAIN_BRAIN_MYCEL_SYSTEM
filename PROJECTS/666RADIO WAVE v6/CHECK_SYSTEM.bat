@echo off
setlocal
cd /d "%~dp0"
echo === SoundwaveStudio 666 System Check ===
call ENSURE_BUILD_TOOLS.bat build
if errorlevel 1 exit /b 1
node tests\deep-integration.test.cjs || exit /b 1
node --check main.js || exit /b 1
node --check preload.js || exit /b 1
node --check src\integration\666-integration.js || exit /b 1
echo PASS: source gates
