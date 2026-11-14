@echo off
setlocal
cd /d "%~dp0"
set "MODE=%~1"

where winget >nul 2>nul || (
  echo FAIL: winget is required for the approved automatic Node.js LTS setup.
  exit /b 2
)

where node >nul 2>nul
if errorlevel 1 (
  echo Installing Node.js LTS through winget...
  winget install --id OpenJS.NodeJS.LTS --exact --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
  if errorlevel 1 (echo FAIL: Node.js LTS installation failed. & exit /b 1)
) else (
  echo Updating Node.js LTS through winget when an update is available...
  winget upgrade --id OpenJS.NodeJS.LTS --exact --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
  if errorlevel 1 echo INFO: No winget-managed update was applied; continuing with the detected Node.js.
)

if exist "%ProgramFiles%\nodejs" set "PATH=%ProgramFiles%\nodejs;%PATH%"
if exist "%APPDATA%\npm" set "PATH=%APPDATA%\npm;%PATH%"
where node >nul 2>nul || (echo FAIL: Node.js is still unavailable after setup. & exit /b 1)
where npm >nul 2>nul || (echo FAIL: npm is unavailable after Node.js setup. & exit /b 1)
node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 20 ? 0 : 1)"
if errorlevel 1 (echo FAIL: Node.js 20 or newer is required. & exit /b 1)

node --version
npm --version
if /i "%MODE%"=="build" (
  echo Synchronizing locked project build tools with npm ci...
  call npm ci
  if errorlevel 1 (echo FAIL: Locked npm dependency installation failed. & exit /b 1)
  call node scripts\ensure-electron-runtime.cjs
  if errorlevel 1 (echo FAIL: Electron runtime verification or repair failed. & exit /b 1)
)
if /i "%MODE%"=="runtime" if not exist "node_modules\electron\dist\electron.exe" (
  echo Installing locked project runtime dependencies...
  call npm ci
  if errorlevel 1 (echo FAIL: Locked npm dependency installation failed. & exit /b 1)
)
if /i "%MODE%"=="runtime" (
  call node scripts\ensure-electron-runtime.cjs
  if errorlevel 1 (echo FAIL: Electron runtime verification or repair failed. & exit /b 1)
)
exit /b 0
