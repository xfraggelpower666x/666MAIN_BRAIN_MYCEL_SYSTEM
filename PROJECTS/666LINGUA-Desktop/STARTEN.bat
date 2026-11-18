@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "EXE=666LINGUA-x64.exe"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "EXE=666LINGUA-ARM64.exe"
if /i "%PROCESSOR_ARCHITEW6432%"=="ARM64" set "EXE=666LINGUA-ARM64.exe"
if "%~1"=="" goto menu
if not "%~2"=="" goto invalid
for %%A in (start browser diagnose repair build test package toolstarter setup all help) do if /i "%~1"=="--%%A" (
  set "ACTION=%%A"
  goto run
)
goto invalid

:menu
echo.
echo            666SOUNDsDESIGn - 666LINGUA WINDOWS
echo.
echo   1  Windows-App starten
echo   2  Im Standardbrowser starten
echo   3  Diagnose und Paketpruefung
echo   4  Release-Dateien lokal reparieren
echo   5  Windows-EXE neu bauen
echo   6  Entwicklertests ausfuehren
echo   7  Portables ZIP erstellen
echo   8  Toolstarter-Projektcheck
echo   9  Ausfuehrbares Windows-Setup erstellen
echo   A  Test, Build, Portable und Setup in einem Lauf
echo   0  Beenden
echo.
"%SystemRoot%\System32\choice.exe" /C 123456789A0 /N /M "Auswahl [1-9, A, 0]: "
if errorlevel 255 goto invalid
if errorlevel 11 (set "RC=0" & goto done)
if errorlevel 10 (set "ACTION=all" & goto run)
if errorlevel 9 (set "ACTION=setup" & goto run)
if errorlevel 8 (set "ACTION=toolstarter" & goto run)
if errorlevel 7 (set "ACTION=package" & goto run)
if errorlevel 6 (set "ACTION=test" & goto run)
if errorlevel 5 (set "ACTION=build" & goto run)
if errorlevel 4 (set "ACTION=repair" & goto run)
if errorlevel 3 (set "ACTION=diagnose" & goto run)
if errorlevel 2 (set "ACTION=browser" & goto run)
if errorlevel 1 (set "ACTION=start" & goto run)
set "RC=1"
goto done

:run
call :action_%ACTION%
set "RC=%ERRORLEVEL%"
if not "%~1"=="" goto done
if /i "%ACTION%"=="start" if "%RC%"=="0" goto done
if /i "%ACTION%"=="browser" if "%RC%"=="0" goto done
echo.
echo Rueckgabecode: %RC%
pause
goto menu

:action_start
call :choose_exe
if errorlevel 1 exit /b 1
start /wait "" "%CD%\%APP_PATH%"
exit /b %ERRORLEVEL%

:action_browser
call :choose_exe
if errorlevel 1 exit /b 1
start /wait "" "%CD%\%APP_PATH%" --browser
exit /b %ERRORLEVEL%

:choose_exe
set "APP_PATH=release\%EXE%"
if exist "%APP_PATH%" exit /b 0
set "APP_PATH=build-output\build\%EXE%"
if exist "%APP_PATH%" exit /b 0
echo %EXE% fehlt. Waehle Build oder Komplettlauf.
exit /b 1

:action_diagnose
call :developer diagnose
exit /b %ERRORLEVEL%
:action_repair
call :developer repair
exit /b %ERRORLEVEL%
:action_build
call :developer build
exit /b %ERRORLEVEL%
:action_test
call :developer test
exit /b %ERRORLEVEL%
:action_package
call :developer package
exit /b %ERRORLEVEL%
:action_toolstarter
call :developer toolstarter
exit /b %ERRORLEVEL%
:action_setup
call :developer setup
exit /b %ERRORLEVEL%
:action_all
call :developer all
exit /b %ERRORLEVEL%

:developer
set "LINGUA_PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "LINGUA_PS=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%LINGUA_PS%" (
  >&2 echo Windows PowerShell is required for Go verification and installation.
  exit /b 1
)
"%LINGUA_PS%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "scripts\windows-go.ps1" "%~1"
exit /b %ERRORLEVEL%

:action_help
echo Optionen: --start --browser --diagnose --repair --build --test --package --toolstarter --setup --all --help
exit /b 0

:invalid
echo Ungueltige Option. STARTEN.bat --help zeigt alle Befehle.
set "RC=2"
:done
popd
if "%~1"=="" if not "%RC%"=="0" pause
exit /b %RC%
