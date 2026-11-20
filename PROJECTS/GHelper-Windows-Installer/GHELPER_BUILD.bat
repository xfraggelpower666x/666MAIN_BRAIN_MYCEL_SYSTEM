@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "BUILD_RC=0"
if /i "%~1"=="installer" goto directBuild
if /i "%~1"=="ausgabe" goto directOutput
if not "%~1"=="" goto usage

:menu
echo.
echo G-Helper - PC-Kompilierung
echo   1 - Werkzeuge aktualisieren und Windows-Setup bauen
echo   2 - Ausgabeordner anzeigen
echo   3 - Beenden
choice /c 123 /n /m "Auswahl: "
set "CHOICE_RC=%ERRORLEVEL%"
if "%CHOICE_RC%"=="3" goto finish
if "%CHOICE_RC%"=="2" goto menuOutput
if "%CHOICE_RC%"=="1" goto menuBuild
set "BUILD_RC=1"
goto finish

:menuBuild
call :build
set "BUILD_RC=%ERRORLEVEL%"
pause
goto menu

:menuOutput
call :showOutput
goto menu

:directBuild
call :build
set "BUILD_RC=%ERRORLEVEL%"
if /i not "%~2"=="/nopause" pause
goto finish

:directOutput
call :showOutput
set "BUILD_RC=%ERRORLEVEL%"
goto finish

:usage
echo Nutzung: GHELPER_BUILD.bat [installer [/nopause] ^| ausgabe]
set "BUILD_RC=1"
goto finish

:build
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap.ps1"
set "STEP_RC=%ERRORLEVEL%"
if not "%STEP_RC%"=="0" echo Build fehlgeschlagen. Exitcode %STEP_RC%.
exit /b %STEP_RC%

:showOutput
if not exist "output\" (
    echo Der Ausgabeordner wird beim ersten erfolgreichen Build erstellt.
    exit /b 1
)
start "" "%SystemRoot%\explorer.exe" "%CD%\output"
exit /b %ERRORLEVEL%

:finish
popd
exit /b %BUILD_RC%
