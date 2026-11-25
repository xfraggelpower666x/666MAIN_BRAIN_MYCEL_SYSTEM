@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul || (echo [FEHLER] Node.js fehlt. & pause & exit /b 1)
where npm >nul 2>nul || (echo [FEHLER] npm fehlt. & pause & exit /b 1)
where python >nul 2>nul || (echo [FEHLER] Python fehlt. & pause & exit /b 1)
if not exist "node_modules\electron" (
 echo [INFO] Electron ist nicht installiert. Keine automatische Netzwerk-Installation.
 echo Bitte bei Zustimmung: npm install
 pause
 exit /b 2
)
call npm start
if errorlevel 1 pause
