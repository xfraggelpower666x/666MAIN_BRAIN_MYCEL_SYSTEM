@echo off
setlocal DisableDelayedExpansion
set "PYTHON="
where py.exe >nul 2>nul
if errorlevel 1 goto fallback
py -3 -c "import tkinter,sys; sys.exit(sys.version_info < (3,10))" >nul 2>nul
if errorlevel 1 goto fallback
py -3 "%~dp0app.py" %*
set "RC=%ERRORLEVEL%"
goto finish
:fallback
where python.exe >nul 2>nul
if errorlevel 1 goto missing
python -c "import tkinter,sys; sys.exit(sys.version_info < (3,10))" >nul 2>nul
if errorlevel 1 goto missing
python "%~dp0app.py" %*
set "RC=%ERRORLEVEL%"
goto finish
:missing
echo Python 3.10 or newer with Tkinter is required.
set "RC=2"
:finish
if "%~1"=="" if not "%RC%"=="0" pause
exit /b %RC%
