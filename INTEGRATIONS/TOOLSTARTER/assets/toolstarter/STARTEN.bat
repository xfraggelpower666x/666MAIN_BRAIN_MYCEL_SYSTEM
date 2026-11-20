@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
py.exe -3 -c "import sys;sys.exit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 goto use_launcher
python.exe -c "import sys;sys.exit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 goto use_python
echo Python 3.10 or later was not found. Install CPython with Tcl/Tk for the graphical window.
set "RC=1"
goto finish
:use_launcher
py.exe -3 "%~dp0toolstarter.py" %*
set "RC=%errorlevel%"
goto finish
:use_python
python.exe "%~dp0toolstarter.py" %*
set "RC=%errorlevel%"
:finish
popd
if not "%RC%"=="0" if "%~1"=="" pause
exit /b %RC%
