@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title 666 CHATBACKUP PC TOOL - ZENTRALES WINDOWS MENUE
:menu
cls
echo =============================================================
echo  666 CHATBACKUP PC TOOL - EINE ANWENDUNG / EIN WINDOWS MENUE
echo  Grundlage v1.10.5 + additive R5.5 Erweiterungen
echo =============================================================
echo.
echo  [1] Original-EXE starten
echo  [2] Original-EXE selbst kompilieren (nur EIN Programm)
echo  [3] Python-Hauptanwendung starten (Entwicklung)
echo  [4] System- und Abhaengigkeitsdiagnose
echo  [5] Build-Umgebung installieren / reparieren
echo  [6] Python-Regressionstests ausfuehren
echo  [7] Release-Integritaet pruefen
echo  [8] Windows-Host-Abnahme (Testdaten, optional Share-Link)
echo  [9] Beenden
echo.
set "WAHL="
set /p "WAHL=Auswahl [1-9]: "
if "%WAHL%"=="1" goto runexe
if "%WAHL%"=="2" goto build
if "%WAHL%"=="3" goto runpy
if "%WAHL%"=="4" goto diag
if "%WAHL%"=="5" goto deps
if "%WAHL%"=="6" goto tests
if "%WAHL%"=="7" goto integrity
if "%WAHL%"=="8" goto acceptance
if "%WAHL%"=="9" exit /b 0
echo Ungueltige Auswahl.
pause
goto menu

:runexe
if not exist "dist\666_CHATBACKUP_PC_TOOL.exe" (
  echo [OFFEN] Noch keine EXE vorhanden. Bitte zuerst Option 2.
  pause
  goto menu
)
start "" "%CD%\dist\666_CHATBACKUP_PC_TOOL.exe"
goto menu

:build
echo [BUILD] Es wird nur 666_CHATBACKUP_PC_TOOL.exe erstellt.
echo Abhaengigkeiten koennen bei Bedarf installiert/aktualisiert werden.
choice /c JN /m "Kompilierung starten"
if errorlevel 2 goto menu
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode Build
if errorlevel 1 goto failed
if not exist ".venv-build\Scripts\python.exe" goto failed
".venv-build\Scripts\python.exe" -m PyInstaller --noconfirm --clean "666_CHATBACKUP_PC_TOOL.spec"
if errorlevel 1 goto failed
if not exist "dist\666_CHATBACKUP_PC_TOOL.exe" goto failed
echo [PASS] dist\666_CHATBACKUP_PC_TOOL.exe
pause
goto menu

:runpy
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode Run -ForceSource
if errorlevel 1 goto failed
goto menu

:diag
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode Audit
if errorlevel 1 goto failed
pause
goto menu

:deps
echo [HINWEIS] Installation/Aktualisierung von Build-Abhaengigkeiten moeglich.
choice /c JN /m "Umgebung jetzt installieren/reparieren"
if errorlevel 2 goto menu
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode Build
if errorlevel 1 goto failed
pause
goto menu

:tests
if exist ".venv-build\Scripts\python.exe" (
  ".venv-build\Scripts\python.exe" -m pytest -q tests
) else (
  py -3 -m pytest -q tests
)
if errorlevel 1 goto failed
pause
goto menu

:integrity
if exist ".venv-build\Scripts\python.exe" (
  ".venv-build\Scripts\python.exe" tests\release_integrity_probe.py
) else (
  py -3 tests\release_integrity_probe.py
)
if errorlevel 1 goto failed
pause
goto menu

:acceptance
echo [HOST] Dieser Test kann echte Share-Links abrufen.
choice /c JN /m "Windows-Host-Test ausfuehren"
if errorlevel 2 goto menu
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\bootstrap\bootstrap.ps1" -Mode VerifyHost
if errorlevel 1 goto failed
pause
goto menu

:failed
echo.
echo [FAIL] Vorgang fehlgeschlagen. Vorhandene Installation nicht ersetzen.
pause
goto menu
