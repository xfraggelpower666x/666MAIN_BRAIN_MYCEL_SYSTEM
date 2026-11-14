@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0"
if errorlevel 1 (
    echo ERROR: Could not open the project folder.
    exit /b 1
)

set "interactive="
if /i "%~1"=="/start" goto start_app
if /i "%~1"=="/check" goto check_only
if /i "%~1"=="/cache" goto build_cache
if not "%~1"=="" goto usage

set "interactive=1"
echo Light Wave Tech - Windows launcher
echo.
echo [1] Start Stereo EQ
echo [2] Check Python and startup files
echo [3] Build the normal video cache
echo [4] Exit
choice /c 1234 /n /m "Select 1-4: "
if errorlevel 255 goto menu_failed
if errorlevel 4 goto menu_exit
if errorlevel 3 goto build_cache
if errorlevel 2 goto check_only
if errorlevel 1 goto start_app
goto menu_exit

:start_app
call :check_start
set "rc=%errorlevel%"
if not "%rc%"=="0" goto finish
"%python_exe%" %python_args% "32-bit_STEREO_EQ__light_wave_tech_v1.1.10.py"
set "rc=%errorlevel%"
if not "%rc%"=="0" echo ERROR: Stereo EQ exited with code %rc%.
goto finish

:check_only
call :check_start
set "rc=%errorlevel%"
if "%rc%"=="0" echo PASS: Python, required modules and startup JSON checked. Media, audio hardware and GPU are checked by the application.
goto finish

:build_cache
call :find_python
set "rc=%errorlevel%"
if not "%rc%"=="0" goto finish
if not exist "CONFIG\config_preload_path_names.py" (
    echo ERROR: CONFIG\config_preload_path_names.py is missing.
    set "rc=3"
    goto finish
)
if not exist "CONFIG\filepaths.json" (
    echo ERROR: CONFIG\filepaths.json is missing.
    set "rc=3"
    goto finish
)
"%python_exe%" %python_args% "CONFIG\config_preload_path_names.py"
set "rc=%errorlevel%"
if not "%rc%"=="0" echo ERROR: Normal cache generation failed with code %rc%. Check your local paths in CONFIG\filepaths.json.
goto finish

:check_start
call :find_python
if errorlevel 1 exit /b 2
if not exist "32-bit_STEREO_EQ__light_wave_tech_v1.1.10.py" (
    echo ERROR: The Stereo EQ entry script is missing.
    exit /b 3
)
if not exist "CONFIG\filepaths.json" (
    echo ERROR: CONFIG\filepaths.json is missing.
    exit /b 3
)
if not exist "CONFIG\preloaded_paths_cache_normal.json" (
    echo ERROR: Normal cache is missing. Configure your media paths and run CACHE_ERSTELLEN.bat.
    exit /b 3
)
"%python_exe%" %python_args% -c "import json; from pathlib import Path; files = ('CONFIG/filepaths.json', 'CONFIG/preloaded_paths_cache_normal.json'); docs = [json.loads(Path(name).read_text(encoding='utf-8')) for name in files]; raise SystemExit(0 if all(isinstance(doc, dict) for doc in docs) else 1)"
if errorlevel 1 (
    echo ERROR: Startup JSON is unreadable or invalid.
    exit /b 3
)
"%python_exe%" %python_args% -c "import cv2, loguru, matplotlib, moderngl, numpy, pandas, pygame.freetype, pygame.sndarray, pyfar, pyloudnorm, qiskit_aer, sounddevice, soundfile, sympy; from PIL import Image; from scipy.io import wavfile; from mutagen.mp3 import MP3; from qiskit import QuantumCircuit"
if errorlevel 1 (
    echo ERROR: A required Python module could not load. Follow HOWTO_SETUP.txt in the selected Python environment.
    exit /b 4
)
exit /b 0

:find_python
set "python_args="
if exist ".venv\Scripts\python.exe" (
    set "python_exe=.venv\Scripts\python.exe"
    call :check_version
    if not errorlevel 1 exit /b 0
)
set "python_exe=python"
call :check_version
if not errorlevel 1 exit /b 0
set "python_exe=py"
set "python_args=-3.10"
call :check_version
if not errorlevel 1 exit /b 0
echo ERROR: Python 3.10 was not found. Activate the project environment or follow HOWTO_SETUP.txt.
exit /b 2

:check_version
"%python_exe%" %python_args% -c "import sys; raise SystemExit(sys.version_info[:2] != (3, 10))" >nul 2>&1
exit /b %errorlevel%

:usage
echo Usage: STARTEN.bat [/start ^| /check ^| /cache]
set "rc=64"
goto finish

:menu_failed
echo ERROR: Menu selection failed.
set "rc=1"
goto finish

:menu_exit
set "rc=0"
set "interactive="

:finish
popd
if defined interactive pause
exit /b %rc%
