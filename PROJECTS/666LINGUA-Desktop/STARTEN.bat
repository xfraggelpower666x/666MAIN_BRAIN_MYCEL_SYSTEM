@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "PREFLIGHT_OK="
if "%~1"=="" goto interactive
if not "%~3"=="" goto invalid
if not "%~2"=="" if /i not "%~2"=="/nopause" goto invalid

set "MODE="
for %%A in (start installer portable check dev windowed browser diagnose repair build test package toolstarter setup all help) do (
  if /i "%~1"=="%%A" set "MODE=%%A"
  if /i "%~1"=="--%%A" set "MODE=%%A"
)
if not defined MODE goto invalid
call :action "%MODE%"
set "RC=%ERRORLEVEL%"
goto finish

:interactive
call :preflight
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto finish

:menu
echo.
echo 666LINGUA Desktop - 666SOUNDsDESIGn
echo   1 - App aus dem Projekt starten
echo   2 - Windows-Installer und portable EXE bauen
echo   3 - Portables ZIP bauen
echo   4 - Ende
echo   5 - Entwicklungsbuild erstellen und direkt starten
echo   6 - Entwicklertests ausfuehren
echo   7 - Im Fenstermodus starten
echo   8 - Projekt und Werkzeuge pruefen
echo   9 - Release und Pruefsummen kontrollieren
echo   A - Vollstaendiges Release bauen
echo   R - Release lokal reparieren
"%SystemRoot%\System32\choice.exe" /c 123456789AR0 /n /m "Auswahl: "
set "SELECTION=%ERRORLEVEL%"
if "%SELECTION%"=="4" goto menuEnd
if "%SELECTION%"=="12" goto menuEnd
if "%SELECTION%"=="0" goto menuCancel
set "MODE="
if "%SELECTION%"=="1" set "MODE=start"
if "%SELECTION%"=="2" set "MODE=installer"
if "%SELECTION%"=="3" set "MODE=portable"
if "%SELECTION%"=="5" set "MODE=dev"
if "%SELECTION%"=="6" set "MODE=test"
if "%SELECTION%"=="7" set "MODE=windowed"
if "%SELECTION%"=="8" set "MODE=check"
if "%SELECTION%"=="9" set "MODE=diagnose"
if "%SELECTION%"=="10" set "MODE=all"
if "%SELECTION%"=="11" set "MODE=repair"
if not defined MODE goto menuError
call :action "%MODE%"
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" echo [OK] %MODE% abgeschlossen.
if not "%RC%"=="0" >&2 echo FEHLER: %MODE% fehlgeschlagen. Exitcode: %RC%.
goto menu

:menuEnd
set "RC=0"
goto finish
:menuCancel
set "RC=130"
goto done
:menuError
>&2 echo FEHLER: Die Menueauswahl ist fehlgeschlagen.
set "RC=1"
goto finish
:invalid
>&2 echo Ungueltige Option. STARTEN.bat --help zeigt alle Befehle.
set "RC=2"
:finish
if not "%RC%"=="0" if /i not "%~2"=="/nopause" pause
:done
popd
exit /b %RC%

:action
if /i "%~1"=="help" goto help
if /i "%~1"=="diagnose" goto diagnose
if /i "%~1"=="toolstarter" goto toolstarter
if /i "%~1"=="check" set "PREFLIGHT_OK="
call :preflight
set "ACTION_RC=%ERRORLEVEL%"
if not "%ACTION_RC%"=="0" exit /b %ACTION_RC%
if /i "%~1"=="check" exit /b 0
if /i "%~1"=="start" goto start
if /i "%~1"=="dev" goto start
if /i "%~1"=="windowed" goto windowed
if /i "%~1"=="browser" goto windowed
if /i "%~1"=="installer" goto installer
if /i "%~1"=="setup" goto installer
if /i "%~1"=="portable" goto portable
if /i "%~1"=="package" goto portable
call :developer "%~1"
exit /b %ERRORLEVEL%

:preflight
if defined PREFLIGHT_OK exit /b 0
echo [SYSTEM] Pruefe 666LINGUA, Go, Electron und die Projekttests.
call :developer check
set "PREFLIGHT_RC=%ERRORLEVEL%"
if not "%PREFLIGHT_RC%"=="0" exit /b %PREFLIGHT_RC%
set "PREFLIGHT_OK=1"
echo PASS: 666LINGUA Systempruefung.
exit /b 0

:start
call :launch
exit /b %ERRORLEVEL%
:windowed
call :launch --windowed
exit /b %ERRORLEVEL%
:launch
call :developer dev
set "LAUNCH_RC=%ERRORLEVEL%"
if not "%LAUNCH_RC%"=="0" exit /b %LAUNCH_RC%
set "APP_PATH=build-output\dev\666LINGUA-x64.exe"
call :artifact "%APP_PATH%" || exit /b 1
echo [START] "%APP_PATH%"
start /wait "" "%CD%\%APP_PATH%" %*
exit /b %ERRORLEVEL%

:installer
call :developer setup
set "BUILD_RC=%ERRORLEVEL%"
if not "%BUILD_RC%"=="0" exit /b %BUILD_RC%
call :artifact "build-output\setup\666LINGUA-Setup.exe" || exit /b 1
call :artifact "build-output\setup\666LINGUA-Portable.exe"
exit /b %ERRORLEVEL%

:portable
call :developer package
set "BUILD_RC=%ERRORLEVEL%"
if not "%BUILD_RC%"=="0" exit /b %BUILD_RC%
call :artifact "build-output\package\666LINGUA-Portable-win-x64.zip"
exit /b %ERRORLEVEL%

:diagnose
call :developer diagnose
exit /b %ERRORLEVEL%
:toolstarter
call :developer toolstarter
exit /b %ERRORLEVEL%

:artifact
if not exist "%~1" (
  >&2 echo FEHLER: Ausgabe fehlt: "%~1"
  exit /b 1
)
echo PASS: "%~1"
exit /b 0

:developer
if not exist "go.mod" (
  >&2 echo FEHLER: go.mod fehlt. Bitte das Entwicklungspaket vollstaendig entpacken.
  exit /b 1
)
if not exist "scripts\windows-go.ps1" (
  >&2 echo FEHLER: scripts\windows-go.ps1 fehlt. Bitte das Entwicklungspaket vollstaendig entpacken.
  exit /b 1
)
set "LINGUA_PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "LINGUA_PS=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%LINGUA_PS%" (
  set "LINGUA_PS="
  for /f "delims=" %%P in ('where.exe pwsh.exe 2^>nul') do if not defined LINGUA_PS set "LINGUA_PS=%%P"
)
if not defined LINGUA_PS (
  >&2 echo FEHLER: Windows PowerShell oder PowerShell 7 fehlt.
  exit /b 1
)
"%LINGUA_PS%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts\windows-go.ps1" "%~1"
exit /b %ERRORLEVEL%

:help
echo Nutzung: STARTEN.bat [start^|installer^|portable^|check] [/nopause]
echo Weitere Optionen: --dev --windowed --diagnose --repair --build --test --toolstarter --all --help
exit /b 0
