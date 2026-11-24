@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666StreamTranscoder v3.0 - Electron UI Preview R12.1
echo ============================================================
echo 666StreamTranscoder v3.0 - Electron Cyber UI Preview R12.1
echo ============================================================
echo.
echo HINWEIS: Nur grafische Vorschau. Kein Livestream, kein Audio.
echo.
where node >nul 2>nul
if errorlevel 1 goto :missing_node
where npm >nul 2>nul
if errorlevel 1 goto :missing_node
echo [INFO] Node:
node --version
echo [INFO] npm:
call npm --version
if errorlevel 1 goto :failed

if exist "node_modules\electron\dist\electron.exe" goto :ready
echo.
echo [INFO] Electron fehlt in diesem Projektordner.
echo npm install installiert Projektpakete in diesem Ordner.
echo Es koennen Downloads erfolgen. Keine globale Installation.
choice /C JN /N /M "Projektabhaengigkeiten jetzt installieren? [J/N] "
if errorlevel 2 goto :cancelled
if not errorlevel 1 goto :cancelled
call npm install --no-audit --no-fund
if errorlevel 1 goto :failed
if not exist "node_modules\electron\dist\electron.exe" goto :failed

:ready
echo.
echo [INFO] Sicherheits-/Quellpruefung...
call npm run check
if errorlevel 1 goto :failed
call npm test
if errorlevel 1 goto :failed
echo.
echo [INFO] Starte nur die Electron-Designvorschau.
call npm start
if errorlevel 1 goto :failed
echo.
echo [INFO] Electron-Vorschau beendet.
exit /b 0

:missing_node
echo [BLOCKIERT] Node.js und npm sind erforderlich.
echo Installiere Node.js LTS und starte diese Datei erneut.
goto :failed
:cancelled
echo [ABGEBROCHEN] Keine Abhaengigkeiten installiert.
exit /b 2
:failed
echo.
echo [BLOCKIERT] Vorschau nicht gestartet. Fehlercode: %errorlevel%
pause
exit /b 1
