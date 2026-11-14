@echo off
setlocal
cd /d "%~dp0"
set "MODE=%~1"

where winget >nul 2>nul || (
  echo FAIL: winget is required for the approved automatic Python host setup.
  exit /b 2
)
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo Installing Python 3.12 through winget...
  winget install --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
  if errorlevel 1 (echo FAIL: Python 3.12 installation failed. & exit /b 1)
  if exist "%LocalAppData%\Programs\Python\Python312" set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
) else (
  echo Updating Python 3.12 through winget when an update is available...
  winget upgrade --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
  if errorlevel 1 echo INFO: No winget-managed update was applied; continuing with detected Python 3.12.
)
py -3.12 --version || (echo FAIL: Python 3.12 is still unavailable. & exit /b 1)
if /i "%MODE%"=="build" (
  echo Updating the current user's PyInstaller installation...
  py -3.12 -m pip install --user --upgrade pyinstaller
  if errorlevel 1 (echo FAIL: PyInstaller installation or update failed. & exit /b 1)
)
exit /b 0
