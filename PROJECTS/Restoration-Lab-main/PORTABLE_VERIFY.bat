@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Restoration Lab - Portable pruefen
set "DIR=%~dp0dist\Restoration Lab"
set "EXE=%DIR%\Restoration Lab.exe"
set "APPLOG=%LOCALAPPDATA%\Restoration Lab\Logs\app.log"
set "FAIL=0"
if not exist "%EXE%" (echo [FAIL] Restoration Lab.exe fehlt. Erst BUILD_PORTABLE_EXE.bat ausfuehren. & set "FAIL=1" & goto result)
if not exist "%DIR%\_internal\assets\User_Guide.html" (echo [FAIL] assets\User_Guide.html fehlt. & set "FAIL=1")
if not exist "%DIR%\_internal\assets\RestorationLab.png" (echo [FAIL] assets\RestorationLab.png fehlt. & set "FAIL=1")
if not exist "%DIR%\_internal\test_assets\decoder_check.mp3" (echo [FAIL] test_assets\decoder_check.mp3 fehlt. & set "FAIL=1")
if not exist "%~dp0Restoration-Lab-3.0-Windows-x64.zip" echo [WARNUNG] ZIP-Datei nicht gefunden.
if "%FAIL%"=="1" goto result
echo [CHECK] Fuehre Selbsttest der gebauten EXE aus (GUI-Programm, wartet bis zum Ende) ...
start "" /wait "%EXE%" --self-test
if errorlevel 1 (echo [FAIL] Selbsttest der EXE fehlgeschlagen. & set "FAIL=1") else (echo [PASS] Selbsttest der EXE bestanden.)
if exist "%APPLOG%" (echo --- app.log, letzte Zeilen --- & powershell -NoProfile -Command "Get-Content -LiteralPath $env:APPLOG -Tail 8")
:result
echo.
if "%FAIL%"=="0" (echo [PASS] Portable-Ordner vollstaendig und lauffaehig.) else (echo [FAIL] Portable-Ordner noch nicht in Ordnung.)
pause
exit /b %FAIL%
