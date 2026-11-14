@echo off
rem Hilfsdatei: sucht Python 3.10-3.14 (64 Bit, Tk 8.6+), legt .venv-gui an, setzt RL_PY.
rem Wird von den anderen .bat-Dateien per CALL aufgerufen. Loescht nie eine Umgebung.
set "RL_PY="
set "BASEPY="
set "VENV=%~dp0.venv-gui"
if exist "%VENV%\Scripts\python.exe" goto check_venv
where py >nul 2>nul
if errorlevel 1 goto try_python
for %%V in (3.13 3.12 3.11 3.14 3.10) do call :try_py %%V
:try_python
if defined BASEPY goto create
where python >nul 2>nul
if errorlevel 1 goto missing
python "%~dp0ENV_CHECK.py" --runtime >nul 2>nul
if not errorlevel 1 set "BASEPY=python"
:create
if not defined BASEPY goto missing
echo [PYTHON] Erstelle .venv-gui mit %BASEPY%
%BASEPY% -m venv "%VENV%"
if errorlevel 1 (echo [FEHLER] Erstellung von .venv-gui fehlgeschlagen. & exit /b 4)
:check_venv
"%VENV%\Scripts\python.exe" "%~dp0ENV_CHECK.py" --runtime
if errorlevel 1 goto incompatible
set "RL_PY=%VENV%\Scripts\python.exe"
exit /b 0
:try_py
if defined BASEPY goto :eof
py -%1 "%~dp0ENV_CHECK.py" --runtime >nul 2>nul
if not errorlevel 1 set "BASEPY=py -%1"
goto :eof
:missing
echo [FEHLT] Kein passendes Python gefunden (3.10-3.14, 64 Bit, mit Tcl/Tk).
echo Bitte Python 3.13 x64 von https://www.python.org/downloads/windows/ installieren
echo (Haken bei "tcl/tk and IDLE" und "py launcher" lassen) und danach erneut starten.
exit /b 2
:incompatible
echo [BLOCKIERT] .venv-gui ist nicht kompatibel. Keine automatische Loeschung.
echo Ordner .venv-gui bitte umbenennen oder loeschen und erneut starten.
exit /b 3
