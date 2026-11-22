@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>&1 || (echo Node.js LTS ist erforderlich. Installiere von https://nodejs.org/ oder via winget install OpenJS.NodeJS.LTS & pause & exit /b 1)
where python >nul 2>&1 || (where py >nul 2>&1 || (echo Python 3 ist erforderlich: winget install Python.Python.3.13 & pause & exit /b 1))
if not exist "node_modules\electron\dist" (
  echo Electron-Abhaengigkeiten werden geprueft und ggf. installiert...
  call npm install --no-audit --no-fund || (pause & exit /b 1)
)
call npm start
if errorlevel 1 pause
