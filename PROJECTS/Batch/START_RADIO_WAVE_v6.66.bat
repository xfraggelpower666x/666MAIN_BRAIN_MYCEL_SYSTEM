@echo off
setlocal
cd /d "%~dp0"
title RADIO WAVE v6.66
echo ============================================================
echo  RADIO WAVE v6.66 - START
echo  Soundwave Core + 666 WebRadio Addon
echo ============================================================
call ENSURE_BUILD_TOOLS.bat runtime
if errorlevel 1 (pause & exit /b 1)
call npm run prepare:branding || (echo Branding preparation failed. & pause & exit /b 1)
call npm run check:radio-wave-release || (echo RADIO WAVE targeted gate failed. & pause & exit /b 1)
call npm start
if errorlevel 1 pause
