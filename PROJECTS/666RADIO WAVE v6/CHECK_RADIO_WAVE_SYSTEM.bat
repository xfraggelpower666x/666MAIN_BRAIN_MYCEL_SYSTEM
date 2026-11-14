@echo off
setlocal
cd /d "%~dp0"
title RADIO WAVE v6.66 - SYSTEM CHECK
echo ============================================================
echo  RADIO WAVE v6.66 - TARGETED SYSTEM CHECK
echo  Historic Soundwave baseline is NOT rerun.
echo ============================================================
call ENSURE_BUILD_TOOLS.bat build
if errorlevel 1 exit /b 1
call npm run prepare:branding || exit /b 1
call npm run check:radio-wave-release || exit /b 1
echo PASS: RADIO WAVE targeted system gates
