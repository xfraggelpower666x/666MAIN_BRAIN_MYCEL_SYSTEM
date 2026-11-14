@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
if "%~1"=="" goto menu
call :action "%~1"
set "RC=%errorlevel%"
if not "%RC%"=="0" if /i not "%~2"=="/nopause" pause
popd
exit /b %RC%

:menu
echo.
echo L.Y.V.R.A. MP3 MANAGER
echo   1 - MP3 Manager starten
echo   2 - System pruefen
echo   3 - Portable EXE bauen
echo   4 - Audio-Tools pruefen oder reparieren
echo   5 - Portable Ordner pruefen
echo   6 - Ende
choice /c 123456 /n /m "Auswahl: "
set "SELECTION=%errorlevel%"
if "%SELECTION%"=="6" goto menuEnd
if "%SELECTION%"=="0" goto menuCancel
if "%SELECTION%"=="255" goto menuError
set "MODE="
if "%SELECTION%"=="1" set "MODE=start"
if "%SELECTION%"=="2" set "MODE=check"
if "%SELECTION%"=="3" set "MODE=build"
if "%SELECTION%"=="4" set "MODE=audio"
if "%SELECTION%"=="5" set "MODE=verify"
if not defined MODE goto menuError
call :action "%MODE%"
set "RC=%errorlevel%"
if "%RC%"=="0" (echo Vorgang abgeschlossen.) else echo Vorgang fehlgeschlagen. Exitcode: %RC%
goto menu

:menuEnd
popd
exit /b 0

:menuCancel
popd
exit /b 130

:menuError
echo FEHLER: Menueauswahl fehlgeschlagen.
popd
exit /b 1

:action
if /i "%~1"=="start" goto start
if /i "%~1"=="check" goto check
if /i "%~1"=="build" goto build
if /i "%~1"=="audio" goto audio
if /i "%~1"=="verify" goto verify
echo Nutzung: L.Y.V.R.A._MP3_MANAGER.bat [start^|check^|build^|audio^|verify] [/nopause]
exit /b 2

:start
if exist "%~dp0L.Y.V.R.A._MP3_MANAGER.exe" goto startPortable
call :ensurePackages runtime || exit /b
set "LOG=%~dp0START_DIAGNOSE.log"
echo === L.Y.V.R.A. STARTDIAGNOSE === > "%LOG%"
echo [START] %DATE% %TIME% >> "%LOG%"
echo [START] GUI wird gestartet. Protokoll: "%LOG%"
"%PY%" SYSTEM_CHECK.py --launch >> "%LOG%" 2>&1
set "RC=%errorlevel%"
type "%LOG%"
exit /b %RC%

:startPortable
"%~dp0L.Y.V.R.A._MP3_MANAGER.exe"
exit /b %errorlevel%

:check
call :ensurePython || exit /b
"%PY%" SYSTEM_CHECK.py
exit /b %errorlevel%

:build
call :ensurePackages build || exit /b
"%PY%" SYSTEM_CHECK.py --build || exit /b
if not exist "dist\L.Y.V.R.A._MP3_MANAGER\L.Y.V.R.A._MP3_MANAGER.exe" (
  echo FEHLER: Portable EXE fehlt.
  exit /b 1
)
echo PASS: dist\L.Y.V.R.A._MP3_MANAGER\L.Y.V.R.A._MP3_MANAGER.exe
echo Den gesamten Portable-Ordner kopieren, nicht nur die EXE.
exit /b 0

:ensurePackages
call :ensurePython || exit /b
if /i "%~1"=="build" goto ensureBuildPackages
"%PY%" SYSTEM_CHECK.py && exit /b 0
choice /c JN /m "Fehlende Pakete nur in .venv_stable installieren"
if errorlevel 2 exit /b 3
"%PY%" SYSTEM_CHECK.py --install || exit /b
"%PY%" SYSTEM_CHECK.py
exit /b %errorlevel%

:ensureBuildPackages
"%PY%" SYSTEM_CHECK.py --build-check && exit /b 0
choice /c JN /m "Fehlende Build-Pakete nur in .venv_stable installieren"
if errorlevel 2 exit /b 3
"%PY%" SYSTEM_CHECK.py --install --build || exit /b
"%PY%" SYSTEM_CHECK.py --build-check
exit /b %errorlevel%

:ensurePython
if not exist "%~dp0SYSTEM_CHECK.py" (
  echo FEHLER: SYSTEM_CHECK.py fehlt. Diese Aktion benoetigt das vollstaendige Quellprojekt.
  exit /b 1
)
set "PY=%~dp0.venv_stable\Scripts\python.exe"
if exist "%PY%" goto checkPython
set "BASEPY="
where py >nul 2>nul
if not errorlevel 1 (
  for %%V in (3.13 3.14 3.12 3.11) do (
    if not defined BASEPY (
      py -%%V -c "import sys; assert (3,11)<=sys.version_info[:2]<=(3,14) and sys.version_info.releaselevel=='final'" >nul 2>nul
      if not errorlevel 1 set "BASEPY=py -%%V"
    )
  )
)
if not defined BASEPY (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; assert (3,11)<=sys.version_info[:2]<=(3,14) and sys.version_info.releaselevel=='final'" >nul 2>nul
    if not errorlevel 1 set "BASEPY=python"
  )
)
if not defined BASEPY (
  echo FEHLER: Stabiles Python 3.11 bis 3.14 fehlt. Bitte Python 3.13 installieren.
  exit /b 2
)
echo [PYTHON] Erstelle getrennte .venv_stable mit %BASEPY%.
%BASEPY% -m venv "%~dp0.venv_stable" || exit /b
:checkPython
"%PY%" -c "import sys; assert (3,11)<=sys.version_info[:2]<=(3,14) and sys.version_info.releaselevel=='final'" >nul 2>nul
if errorlevel 1 (
  echo FEHLER: .venv_stable ist ungueltig. Bitte manuell pruefen oder umbenennen.
  exit /b 3
)
exit /b 0

:audio
set "FFMPEG="
set "FFPROBE="
if exist "%~dp0tools\ffmpeg.exe" if exist "%~dp0tools\ffprobe.exe" (
  set "FFMPEG=%~dp0tools\ffmpeg.exe"
  set "FFPROBE=%~dp0tools\ffprobe.exe"
)
if defined FFMPEG goto audioCheck
if exist "%~dp0ffmpeg.exe" if exist "%~dp0ffprobe.exe" (
  set "FFMPEG=%~dp0ffmpeg.exe"
  set "FFPROBE=%~dp0ffprobe.exe"
)
if defined FFMPEG goto audioCheck
where ffmpeg >nul 2>nul || goto audioMissing
where ffprobe >nul 2>nul || goto audioMissing
set "FFMPEG=ffmpeg"
set "FFPROBE=ffprobe"
:audioCheck
"%FFMPEG%" -hide_banner -encoders 2>nul | findstr /i /c:"libmp3lame" >nul
if errorlevel 1 (echo FEHLER: FFmpeg oder libmp3lame nicht nutzbar. & exit /b 1)
"%FFPROBE%" -version >nul 2>nul
if errorlevel 1 (echo FEHLER: FFprobe nicht nutzbar. & exit /b 1)
echo PASS: FFmpeg, FFprobe und libmp3lame.
exit /b 0

:audioMissing
echo FFmpeg oder FFprobe fehlt. Die Installation benoetigt Internet und Zustimmung.
where winget >nul 2>nul || (echo FEHLER: WinGet fehlt. Bitte Audio-Tools selbst installieren. & exit /b 1)
choice /c JN /m "FFmpeg via WinGet installieren"
if errorlevel 2 exit /b 3
winget install --id Gyan.FFmpeg --exact --accept-source-agreements --accept-package-agreements || exit /b
where ffmpeg >nul 2>nul || goto audioRestart
where ffprobe >nul 2>nul || goto audioRestart
set "FFMPEG=ffmpeg"
set "FFPROBE=ffprobe"
goto audioCheck

:audioRestart
echo Installation ausgefuehrt, aber die Audio-Tools sind noch nicht im PATH.
echo Bitte CMD neu starten und Audio-Tools erneut pruefen.
exit /b 4

:verify
set "VERIFY=%~dp0dist\L.Y.V.R.A._MP3_MANAGER\PORTABLE_VERIFY.ps1"
if exist "%~dp0L.Y.V.R.A._MP3_MANAGER.exe" set "VERIFY=%~dp0PORTABLE_VERIFY.ps1"
if not exist "%VERIFY%" (echo FEHLER: Portable-Pruefskript fehlt: "%VERIFY%" & exit /b 1)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%VERIFY%"
exit /b %errorlevel%
