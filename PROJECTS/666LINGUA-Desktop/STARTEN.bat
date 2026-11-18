@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "DEV_ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "DEV_ARCH=arm64"
if /i "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "DEV_ARCH=arm64"
set "EXE=666LINGUA-x64.exe"
if /i "%DEV_ARCH%"=="arm64" set "EXE=666LINGUA-ARM64.exe"
if "%~1"=="" goto menu
if not "%~3"=="" goto invalid
if not "%~2"=="" if /i not "%~2"=="/nopause" goto invalid
set "ACTION="
for %%A in (start browser windowed dev check diagnose repair build test package toolstarter setup all help installer portable) do (
  if /i "%~1"=="%%A" set "ACTION=%%A"
  if /i "%~1"=="--%%A" set "ACTION=%%A"
)
if not defined ACTION goto invalid
if /i "%ACTION%"=="windowed" set "ACTION=browser"
if /i "%ACTION%"=="installer" set "ACTION=setup"
if /i "%ACTION%"=="portable" set "ACTION=package"
call :run
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" if /i not "%~2"=="/nopause" pause
goto done

:menu
echo.
echo 666LINGUA Desktop - 666SOUNDsDESIGn
echo   1  Fertige Windows-App starten
echo   2  Im Fenstermodus starten
echo   3  Release und Pruefsummen kontrollieren
echo   4  Release lokal reparieren
echo   5  Entwicklungsbuild erstellen und direkt starten
echo   6  Entwicklertests ausfuehren
echo   7  Portable ZIPs fuer x64 und ARM64 bauen
echo   8  Projekt und Go pruefen
echo   9  Windows-Pakete mit Setup und Portable-App bauen
echo   A  Vollstaendiges Release bauen
echo   0  Ende
echo.
"%SystemRoot%\System32\choice.exe" /C 123456789A0 /N /M "Auswahl: "
set "SELECTION=%ERRORLEVEL%"
if "%SELECTION%"=="11" (set "RC=0" & goto done)
if "%SELECTION%"=="0" (set "RC=130" & goto done)
set "ACTION="
if "%SELECTION%"=="1" set "ACTION=start"
if "%SELECTION%"=="2" set "ACTION=browser"
if "%SELECTION%"=="3" set "ACTION=diagnose"
if "%SELECTION%"=="4" set "ACTION=repair"
if "%SELECTION%"=="5" set "ACTION=dev"
if "%SELECTION%"=="6" set "ACTION=test"
if "%SELECTION%"=="7" set "ACTION=package"
if "%SELECTION%"=="8" set "ACTION=check"
if "%SELECTION%"=="9" set "ACTION=setup"
if "%SELECTION%"=="10" set "ACTION=all"
if not defined ACTION (
  >&2 echo FEHLER: Die Menueauswahl ist fehlgeschlagen.
  set "RC=1"
  pause
  goto done
)
call :run
goto menu

:run
echo.
echo [SYSTEM] 666LINGUA: %ACTION%
call :action_%ACTION%
set "ACTION_RC=%ERRORLEVEL%"
if "%ACTION_RC%"=="0" echo [OK] Vorgang abgeschlossen.
if not "%ACTION_RC%"=="0" >&2 echo FEHLER: %ACTION% fehlgeschlagen. Exitcode: %ACTION_RC%
exit /b %ACTION_RC%

:action_start
call :choose_exe
if errorlevel 1 exit /b 1
echo [START] "%APP_PATH%"
start /wait "" "%CD%\%APP_PATH%"
exit /b %ERRORLEVEL%

:action_browser
call :choose_exe
if errorlevel 1 exit /b 1
echo [START] "%APP_PATH%" im Fenstermodus
start /wait "" "%CD%\%APP_PATH%" --windowed
exit /b %ERRORLEVEL%

:choose_exe
set "APP_PATH=release\%EXE%"
if exist "%APP_PATH%" exit /b 0
set "APP_PATH=build-output\build\%EXE%"
if exist "%APP_PATH%" exit /b 0
set "APP_PATH=build-output\dev\%EXE%"
if exist "%APP_PATH%" exit /b 0
echo %EXE% fehlt. Waehle Build oder Komplettlauf.
exit /b 1

:action_diagnose
call :developer diagnose
exit /b %ERRORLEVEL%
:action_repair
call :developer repair
exit /b %ERRORLEVEL%
:action_dev
call :developer dev-%DEV_ARCH%
if not "%ERRORLEVEL%"=="0" exit /b %ERRORLEVEL%
echo [START] "build-output\dev\%EXE%"
start /wait "" "%CD%\build-output\dev\%EXE%"
exit /b %ERRORLEVEL%
:action_build
call :developer build
exit /b %ERRORLEVEL%
:action_test
call :developer test
exit /b %ERRORLEVEL%
:action_package
call :developer package || exit /b
for %%F in (666LINGUA-Windows-x64.zip 666LINGUA-Windows-ARM64.zip) do (
  call :artifact "build-output\package\%%F" || exit /b
)
exit /b 0
:action_check
call :developer check
exit /b %ERRORLEVEL%
:action_toolstarter
call :developer toolstarter
exit /b %ERRORLEVEL%
:action_setup
call :developer setup || exit /b
for %%F in (666LINGUA-Setup-x64.exe 666LINGUA-Setup-ARM64.exe 666LINGUA-Windows-x64.zip 666LINGUA-Windows-ARM64.zip) do (
  call :artifact "build-output\setup\%%F" || exit /b
)
exit /b 0
:action_all
call :developer all
exit /b %ERRORLEVEL%

:artifact
if not exist "%~1" (
  >&2 echo FEHLER: Ausgabe fehlt: "%~1"
  exit /b 1
)
echo [OK] "%~1"
exit /b 0

:developer
if not exist "go.mod" (
  >&2 echo FEHLER: go.mod fehlt. Bitte den vollstaendigen Projektordner entpacken.
  exit /b 1
)
if not exist "scripts\windows-go.ps1" (
  >&2 echo FEHLER: scripts\windows-go.ps1 fehlt. Bitte den vollstaendigen Projektordner entpacken.
  exit /b 1
)
echo [PRUEFUNG] PowerShell und Go fuer %~1
set "LINGUA_PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "LINGUA_PS=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%LINGUA_PS%" (
  >&2 echo Windows PowerShell is required for Go verification and installation.
  exit /b 1
)
"%LINGUA_PS%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts\windows-go.ps1" "%~1"
exit /b %ERRORLEVEL%

:action_help
echo Nutzung: STARTEN.bat [start^|dev^|check^|installer^|portable] [/nopause]
echo Weitere Optionen: --windowed --diagnose --repair --build --test --toolstarter --all --help
echo --setup und installer sind gleich. --package und portable sind gleich.
exit /b 0

:invalid
echo Ungueltige Option. STARTEN.bat --help zeigt alle Befehle.
set "RC=2"
if /i not "%~2"=="/nopause" pause
:done
popd
exit /b %RC%
