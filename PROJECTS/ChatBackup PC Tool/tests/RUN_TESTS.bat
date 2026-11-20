@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
title 666 ChatBackup PC Tool - Tests

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode Audit
if errorlevel 1 goto :failed

where py >nul 2>&1
if not errorlevel 1 (
  py -3 "tests\run_tests.py"
) else (
  python "tests\run_tests.py"
)
if errorlevel 1 goto :failed

echo.
echo TESTS PASSED
pause
exit /b 0

:failed
echo.
echo TESTS FAILED
pause
exit /b 1
