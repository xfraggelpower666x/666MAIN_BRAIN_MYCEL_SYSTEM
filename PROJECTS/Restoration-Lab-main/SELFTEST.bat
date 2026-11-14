@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Selbsttest (Quellcode)
call "%~dp0PYTHON_STABLE.bat"
if errorlevel 1 (pause & exit /b 2)
"%RL_PY%" windows_entry.py --self-test
set "RESULT=%ERRORLEVEL%"
if "%RESULT%"=="0" (echo [PASS] Selbsttest bestanden.) else (echo [FAIL] Selbsttest fehlgeschlagen, Code %RESULT%.)
pause
exit /b %RESULT%
