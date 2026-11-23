@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%~dp0"
set "ENV=%ROOT%.venv\Scripts\python.exe"
set "MANAGER=%ROOT%TOOLS\WINDOWS_TOOL_MANAGER.ps1"
set "READBACK=%ROOT%WINDOWS_ABNAHME\RUN_WINDOWS_READBACK.ps1"
if not exist "%MANAGER%" (
 echo [FEHLER] Tool-Manager fehlt: "%MANAGER%"
 pause
 exit /b 1
)
rem Normaler Doppelklick startet das gemeinsame D-Hauptsystem direkt.
rem Historisches WINDOWS MENUE 7 bleibt mit --menu erreichbar oder bei fehlender Umgebung.
if /I "%~1"=="--menu" goto MENU
if exist "%ENV%" (
 "%ENV%" -c "import klrw, psutil, tkinter" >nul 2>nul
 if not errorlevel 1 (
   call :START_CENTER D
   if not errorlevel 1 goto END
   echo [HINWEIS] Unified-Start fehlgeschlagen. Recovery-Menue wird angezeigt.
 )
)
:MENU
cls
echo ==============================================================
echo  KEYBOARD LED REMAPPER R18 - 666 CYBER DRIVE CONTROL
 echo  WINDOWS MENUE 7 - Kompatibilitaetsfunktionen weiter erreichbar
 echo  Ein Batch-Einstieg / lokale virtuelle Python-Umgebung
 echo  Kein Treiberinstall / kein Tastatur-LED-Schreibzugriff
 echo ==============================================================
echo.
echo  [1] Diagnose ALLER Tools und Abhaengigkeiten
 echo  [2] Fehlende Tools installieren / Umgebung reparieren
 echo  [3] Python- und Projekttools AKTUALISIEREN
 echo  [4] Gemeinsames Windows-System-Tray starten
 echo  [5] Vorschau ohne Tray starten
 echo  [6] Komplette Python-Regression starten
 echo  [7] Windows-Abnahme / JSON-Readback
 echo  [8] Windows-Abnahme: nur Tool- und Importpruefung
 echo  [9] System-Dashboard
 echo  [A] Hauptsystem - Kapazitaet
 echo  [B] Hauptsystem - Klassik
 echo  [C] Hauptsystem - Tools und Recovery
 echo  [D] HAUPTSYSTEM: 666 CYBER DRIVE CONTROL (Alle Bereiche)
 echo  [E] Hauptsystem - Laufwerke / Tray / Overlay
 echo  [0] Beenden
 echo.
choice /c 123456789ABCDE0 /n /m "Auswahl: "
if errorlevel 15 goto END
if errorlevel 14 goto WORKSPACE
if errorlevel 13 goto DRIVE_LED
if errorlevel 12 goto RECOVERY
if errorlevel 11 goto CLASSIC
if errorlevel 10 goto CAPACITY
if errorlevel 9 goto DASHBOARD
if errorlevel 8 goto CHECK_READBACK
if errorlevel 7 goto READBACK
if errorlevel 6 goto TESTS
if errorlevel 5 goto PREVIEW
if errorlevel 4 goto TRAY
if errorlevel 3 goto UPDATE
if errorlevel 2 goto SETUP
if errorlevel 1 goto DIAG
:WORKSPACE
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
call :START_CENTER E
goto PAUSE_MENU
:DRIVE_LED
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
call :START_CENTER D
if errorlevel 1 (
 echo [HINWEIS] Hauptsystem nicht verfuegbar. Starte nur auf diesen Fehler hin den erhaltenen D-Einzelmodus.
 "%ENV%" -m klrw.drive_led_window
)
goto PAUSE_MENU
:RECOVERY
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
call :START_CENTER C
goto PAUSE_MENU
:DIAG
call :TOOLACTION Diagnose
goto PAUSE_MENU
:SETUP
call :TOOLACTION Setup
goto PAUSE_MENU
:UPDATE
call :TOOLACTION Update
goto PAUSE_MENU
:TRAY
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
"%ENV%" -c "import pystray, PIL" >nul 2>nul
if errorlevel 1 (echo [FEHLT] Tray-Pakete. Menuepunkt 2 zur Reparatur nutzen.& goto PAUSE_MENU)
if not exist "%ROOT%TOOLS\REPORTS" mkdir "%ROOT%TOOLS\REPORTS"
set "TRAYLOG=%ROOT%TOOLS\REPORTS\TRAY_LAUNCH_LAST.log"
echo [INFO] Starte Tray; Start- und Laufzeitfehler stehen in:
echo        "%TRAYLOG%"
echo [INFO] Solange Tray/Fenster laeuft, bleibt die Konsole im Startprozess.
"%ENV%" -u -m klrw.unified_tray >"%TRAYLOG%" 2>&1
set "TRAYEXIT=%errorlevel%"
if not "%TRAYEXIT%"=="0" (
 echo [FEHLER] Tray-Start oder Laufzeit fehlgeschlagen, Exit-Code: %TRAYEXIT%
 echo [FEHLER] Protokollausgabe:
 type "%TRAYLOG%"
 echo [HINWEIS] Als Gegenprobe Menuepunkt 5 ohne Tray verwenden.
) else (
 echo [INFO] Tray-/Fensterprozess beendet. Protokoll: "%TRAYLOG%"
)
goto PAUSE_MENU
:PREVIEW
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
"%ENV%" -m klrw.unified_tray --preview --no-tray
goto PAUSE_MENU
:TESTS
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
"%ENV%" -m pytest -q
if errorlevel 1 echo [FEHLER] Regression fehlgeschlagen.
goto PAUSE_MENU
:READBACK
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%READBACK%" -PythonExe "%ENV%"
goto PAUSE_MENU
:CHECK_READBACK
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%READBACK%" -PythonExe "%ENV%" -PreviewOnly
goto PAUSE_MENU
:DASHBOARD
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
"%ENV%" -m klrw.dashboard_window
goto PAUSE_MENU
:CAPACITY
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
call :START_CENTER A
goto PAUSE_MENU
:CLASSIC
call :REQUIRE_READY
if errorlevel 1 goto PAUSE_MENU
call :START_CENTER B
goto PAUSE_MENU
:START_CENTER
if not exist "%ROOT%TOOLS\REPORTS" mkdir "%ROOT%TOOLS\REPORTS"
set "CENTERLOG=%ROOT%TOOLS\REPORTS\CONTROL_CENTER_LAST.log"
echo [INFO] R18 Cyber Control Center startet mit Bereich %~1
"%ENV%" -u -m klrw.control_center --tab %~1 >"%CENTERLOG%" 2>&1
if errorlevel 1 (
 echo [FEHLER] R18 Control Center nicht erfolgreich beendet. Bericht:
 type "%CENTERLOG%"
)
exit /b %errorlevel%
:TOOLACTION
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%MANAGER%" -Action %~1
if errorlevel 1 echo [HINWEIS] Aktion nicht vollstaendig abgeschlossen. Diagnose/Protokoll lesen.
exit /b %errorlevel%
:REQUIRE_READY
if not exist "%ENV%" (
 echo [FEHLT] Lokales Python-Environment. Menuepunkt 2 ausfuehren.
 exit /b 1
)
"%ENV%" -c "import sys, klrw, psutil; assert sys.version_info >= (3,10)" >nul 2>nul
if errorlevel 1 (
 echo [FEHLER] Python/Projekt unvollstaendig. Menuepunkt 2 repariert die lokale .venv.
 exit /b 1
)
exit /b 0
:PAUSE_MENU
 echo.
pause
goto MENU
:END
endlocal
exit /b 0
