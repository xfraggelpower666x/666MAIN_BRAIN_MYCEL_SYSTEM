@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "EXIT_CODE=0"
if /i "%~1"=="mcp" set "STDIO_MODE=1"

call :preflight
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto finish
)

if "%~1"=="" goto menu
if /i "%~1"=="check" goto checked
if /i "%~1"=="install" goto install
if /i "%~1"=="mcp" goto mcp
if /i "%~1"=="start" goto start
goto usage

:menu
echo.
echo Suno Manager
echo   1 - Web UI starten
echo   2 - MCP-Server starten (stdio)
echo   3 - Python-Abhaengigkeiten installieren
echo   4 - Beenden
choice /c 1234 /n /m "Auswahl: "
set "SELECTION=%errorlevel%"
if "%SELECTION%"=="4" goto finish
if "%SELECTION%"=="3" goto install
if "%SELECTION%"=="2" goto mcp
if "%SELECTION%"=="1" goto start
echo FEHLER: Menueauswahl fehlgeschlagen.
set "EXIT_CODE=1"
goto finish

:checked
echo PASS: Suno Manager Projektdateien und Python gefunden.
goto finish

:install
echo [INFO] Installiere requirements.txt...
call :python -m pip install -r requirements.txt
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto finish
)
echo PASS: Abhaengigkeiten installiert.
goto menu

:mcp
call :checkMcp
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto finish
)
>&2 echo [INFO] Starte MCP-Server ueber stdio.
call :python suno_mcp_server.py
set "EXIT_CODE=%errorlevel%"
goto finish

:start
call :checkManager
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto finish
)
set "PORT="
set "RELOAD=--reload"
:parseArgs
if "%~1"=="" goto resolvePort
if /i "%~1"=="start" (
    shift
    goto parseArgs
)
if /i "%~1"=="--port" (
    if "%~2"=="" goto usage
    set "PORT=%~2"
    shift
    shift
    goto parseArgs
)
if /i "%~1"=="--no-reload" (
    set "RELOAD="
    shift
    goto parseArgs
)
goto usage

:resolvePort
if defined PORT goto runManager
if not exist "config.yaml" goto defaultPort
if /i "%PY_LAUNCHER%"=="py" (
    for /f "usebackq delims=" %%P in (`py -3 -c "import yaml; print((yaml.safe_load(open('config.yaml', encoding='utf-8')) or {}).get('server', {}).get('port', 8080))" 2^>nul`) do set "PORT=%%P"
) else (
    for /f "usebackq delims=" %%P in (`python -c "import yaml; print((yaml.safe_load(open('config.yaml', encoding='utf-8')) or {}).get('server', {}).get('port', 8080))" 2^>nul`) do set "PORT=%%P"
)
if not defined PORT goto defaultPort
goto runManager

:defaultPort
set "PORT=8080"

:runManager
echo.
echo Suno Manager wird gestartet
echo   Web UI:  http://localhost:%PORT%
echo   Swagger: http://localhost:%PORT%/docs
echo   Reload:  %RELOAD%
echo.
if defined RELOAD (
    call :python -m uvicorn app:app --host 0.0.0.0 --port %PORT% --reload --log-level info
) else (
    call :python -m uvicorn app:app --host 0.0.0.0 --port %PORT% --log-level info
)
set "EXIT_CODE=%errorlevel%"
goto finish

:checkManager
call :python -c "import fastapi, uvicorn, yaml"
if errorlevel 1 (
    echo FEHLER: Manager-Abhaengigkeiten fehlen. Waehle im Menue Installieren oder fuehre aus:
    echo   python -m pip install -r requirements.txt
    exit /b 1
)
exit /b 0

:checkMcp
call :python -c "import mcp, httpx, dotenv"
if errorlevel 1 (
    >&2 echo FEHLER: MCP-Abhaengigkeiten fehlen. Waehle im Menue Installieren oder fuehre aus:
    >&2 echo   python -m pip install -r requirements.txt
    exit /b 1
)
exit /b 0

:preflight
if not exist "app.py" (>&2 echo FEHLER: app.py fehlt. Bitte den vollstaendigen Projektordner verwenden. & exit /b 1)
if not exist "requirements.txt" (>&2 echo FEHLER: requirements.txt fehlt. & exit /b 1)
if not exist "suno_mcp_server.py" (>&2 echo FEHLER: suno_mcp_server.py fehlt. & exit /b 1)
where py.exe >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
    if not errorlevel 1 (
        set "PY_LAUNCHER=py"
        exit /b 0
    )
)
where python.exe >nul 2>nul
if not errorlevel 1 (
    python.exe -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
    if not errorlevel 1 (
        set "PY_LAUNCHER=python"
        exit /b 0
    )
)
>&2 echo FEHLER: Python 3.10 oder neuer fehlt. Installiere Python und aktiviere "Add Python to PATH".
exit /b 1

:python
if /i "%PY_LAUNCHER%"=="py" (
    py -3 %*
) else (
    python %*
)
exit /b %errorlevel%

:usage
echo Nutzung:
echo   START_SUNO_MANAGER.bat
echo   START_SUNO_MANAGER.bat start [--port PORT] [--no-reload]
echo   START_SUNO_MANAGER.bat mcp
echo   START_SUNO_MANAGER.bat install
echo   START_SUNO_MANAGER.bat check
set "EXIT_CODE=2"
goto finish

:finish
if not "%EXIT_CODE%"=="0" if not defined STDIO_MODE pause
popd
exit /b %EXIT_CODE%
