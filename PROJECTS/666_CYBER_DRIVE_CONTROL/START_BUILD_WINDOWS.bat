@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD\BUILD_CONTROL.ps1"
set "KLRW_EXIT=%ERRORLEVEL%"
echo.
echo 666 CYBER DRIVE CONTROL - Build-Steuerung beendet, Exitcode %KLRW_EXIT%.
pause
exit /b %KLRW_EXIT%
