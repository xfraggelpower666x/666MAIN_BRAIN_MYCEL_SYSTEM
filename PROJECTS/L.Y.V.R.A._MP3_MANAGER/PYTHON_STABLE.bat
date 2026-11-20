@echo off
rem Stabile Projektumgebung: Python 3.11-3.14. Alte .venv niemals veraendern.
set "STABLE=%~dp0.venv_stable\Scripts\python.exe"
if exist "%STABLE%" (
 "%STABLE%" -c "import sys; assert (3,11)<=sys.version_info[:2]<=(3,14) and sys.version_info.releaselevel=='final'" >nul 2>nul
 if not errorlevel 1 (echo [PYTHON] Bestehende stabile Umgebung gefunden. & exit /b 0)
 echo [BLOCKIERT] .venv_stable ist nicht kompatibel. Keine automatische Loeschung.
 echo Bitte .venv_stable manuell pruefen/umbenennen, bevor sie neu erstellt wird.
 exit /b 3
)
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
 echo [FEHLT] Keine unterstuetzte stabile Python-Version gefunden.
 echo Python 3.15.0a8 wird absichtlich NICHT verwendet.
 echo Bitte Python 3.13 64-Bit installieren: https://www.python.org/downloads/windows/
 echo Anschliessend STARTEN.bat erneut ausfuehren.
 exit /b 2
)
echo [PYTHON] Gewaehlt: %BASEPY%
echo [SYSTEM] Neue, getrennte .venv_stable wird erstellt.
%BASEPY% -m venv "%~dp0.venv_stable"
if errorlevel 1 (echo [FEHLER] Erstellung .venv_stable fehlgeschlagen. & exit /b 4)
"%STABLE%" -c "import sys; assert (3,11)<=sys.version_info[:2]<=(3,14) and sys.version_info.releaselevel=='final'"
if errorlevel 1 (echo [FEHLER] Stabile Laufzeit konnte nicht verifiziert werden. & exit /b 5)
exit /b 0
