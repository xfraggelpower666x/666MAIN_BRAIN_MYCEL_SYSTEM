# R13 MENU3 – Windows Path Handoff / Repair & Re-Audit

**Quelle:** R13 MENU2 plus Windows-Fehlerbericht vom 21.11.2026:
`Resolve-Path : Illegales Zeichen im Pfad` bei `TOOLS/WINDOWS_TOOL_MANAGER.ps1:8` nach Auswahl 1, mit `ProjectRoot` als abschliessend inkonsistent gequotetem `B:\Desktop\KeyboardLEDRemapper-Windows-R13-MENU2`.

## B-06 (HOCH) – Native PowerShell-Argument-Quoting

**Ist:** MENU2 `START_WINDOWS_MENUE.bat`, Funktion `:TOOLACTION`, uebersandte `-ProjectRoot "%ROOT%"` mit `%ROOT%=%~dp0` (trailing backslash). CMD/Windows PowerShell 5.1 Argumenttransformation kann den Abschluss-Quote zum Bestandteil des Pfades machen. `Resolve-Path` verwirft diesen; Diagnose/Setup/Update werden blockiert.

**Repair:** Root wird aus dem Pfad des Toolmanagers selbst aufgeloest (`Split-Path -Parent $PSScriptRoot`). CMD uebergibt nur das Aktion-Argument, ohne Dateisystempfad als natives Argument. Optionaler `ProjectRoot` bleibt fuer manuelles Aufrufen erhalten. Die Projektsicherung MENU2 bleibt unveraendert.

**Gegenprobe:** Bestehende Regression + neue Statische Pfad- und Menuevertraege. Exakte Native-Windows-Reproduktion mit PowerShell 5.1 ist hier nicht moeglich: `READBACK_PENDING`.

## Bedienung

1. Neues ZIP *vollstaendig* entpacken, **nicht im alten MENU2-Verzeichnis drueberkopieren**.
2. `START_WINDOWS_MENUE.bat` starten, **Menuepunkt 1** waehlen.
3. Fehlendes Python / Projektpakete: **Menuepunkt 2** freigeben.
4. Bericht: `TOOLS/REPORTS/TOOL_REPORT_*.json`.

Keine Treiberwrites, kein Zugriff auf fremde EXE-Dateien, kein Loeschen alter Versionen.
