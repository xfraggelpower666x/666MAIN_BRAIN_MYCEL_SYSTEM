@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
title Restoration Lab
call :preflight
if errorlevel 1 (
  set "RC=%ERRORLEVEL%"
  goto finish
)
if "%~1"=="" goto menu
call :action "%~1"
set "RC=%ERRORLEVEL%"
goto finish

:menu
echo.
echo RESTORATION LAB 3.0
echo   1 - Restoration Lab starten
echo   2 - Laufzeit und Audio pruefen
echo   3 - Tests ausfuehren
echo   4 - Windows-Paket bauen
echo   5 - Portable Paket pruefen
echo   6 - Ende
choice /c 123456 /n /m "Auswahl: "
set "SELECTION=%ERRORLEVEL%"
if "%SELECTION%"=="6" goto finishSuccess
if "%SELECTION%"=="0" goto menuError
set "MODE="
if "%SELECTION%"=="1" set "MODE=start"
if "%SELECTION%"=="2" set "MODE=check"
if "%SELECTION%"=="3" set "MODE=test"
if "%SELECTION%"=="4" set "MODE=build"
if "%SELECTION%"=="5" set "MODE=verify"
if not defined MODE goto menuError
echo.
call :action "%MODE%"
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" (echo Vorgang abgeschlossen.) else echo Vorgang fehlgeschlagen. Exitcode: %RC%
goto menu

:action
if /i "%~1"=="start" goto startApp
if /i "%~1"=="check" goto checkRuntime
if /i "%~1"=="test" goto runTests
if /i "%~1"=="build" goto buildPackage
if /i "%~1"=="verify" goto verifyPackage
echo Nutzung: RESTORATION_LAB.bat [start^|check^|test^|build^|verify]
exit /b 2

:preflight
echo [SYSTEM] Pruefe Restoration-Lab-Projektdateien.
for %%F in (app.py requirements.txt STARTEN.bat PYTHON_STABLE.bat ENV_CHECK.py TESTS.bat BUILD_PORTABLE_EXE.bat Build-Windows.ps1 PORTABLE_VERIFY.bat) do (
  if not exist "%%~F" (
    echo FEHLER: %%~F fehlt. Bitte den vollstaendigen Projektordner verwenden.
    exit /b 1
  )
)
exit /b 0

:startApp
call "%~dp0STARTEN.bat"
exit /b %ERRORLEVEL%

:checkRuntime
call "%~dp0PYTHON_STABLE.bat"
if errorlevel 1 exit /b %ERRORLEVEL%
"%RL_PY%" ENV_CHECK.py --deps
if errorlevel 1 exit /b %ERRORLEVEL%
"%RL_PY%" ENV_CHECK.py --audio
exit /b %ERRORLEVEL%

:runTests
call "%~dp0TESTS.bat"
exit /b %ERRORLEVEL%

:buildPackage
call "%~dp0BUILD_PORTABLE_EXE.bat"
exit /b %ERRORLEVEL%

:verifyPackage
call "%~dp0PORTABLE_VERIFY.bat"
exit /b %ERRORLEVEL%

:menuError
echo FEHLER: Die Menueauswahl ist fehlgeschlagen.
set "RC=1"
goto finish

:finishSuccess
set "RC=0"
:finish
popd
exit /b %RC%
