@echo off
setlocal
cd /d "%~dp0"
title RADIO WAVE v6.66 - NSIS BUILD
echo ============================================================
echo  RADIO WAVE v6.66 - WINDOWS NSIS INSTALLER BUILD
echo ============================================================
call ENSURE_BUILD_TOOLS.bat build
if errorlevel 1 (pause & exit /b 1)
echo [2/2] Preparing, validating, and building the unsigned NSIS installer...
call npm run dist:unsigned
if errorlevel 1 (echo NSIS BUILD FAILED & pause & exit /b 1)
if not exist "dist\RADIO-WAVE-v6.66-Setup.exe" (echo INSTALLER OUTPUT MISSING & pause & exit /b 1)
echo.
echo BUILD PASS
echo Installer: dist\RADIO-WAVE-v6.66-Setup.exe
echo SHA-256 manifest: dist\RELEASE_ARTIFACT_SHA256SUMS.txt
echo Note: the installer is unsigned unless a code-signing certificate is configured.
echo.
pause
