# R13 MENU-6 — Installer-Repair-Audit

## Reproduzierter Windows-Befund
`Auswahl: 2` -> `winget install Python.Python.3.13` -> `READBACK_PENDING` -> `System.Object[]` kann nicht in `System.Collections.Hashtable` umgewandelt werden.

## Ursache und Fundstelle
`TOOLS/WINDOWS_TOOL_MANAGER.ps1`, Funktion `Ensure-Python`: PowerShell leitet ungebundene Pipeline-Ausgabe nativer Prozesse automatisch als Rueckgabewerte der Funktion weiter. `winget`-Text wurde dadurch mit dem `choice`-Objekt vermischt. Der naechste Aufruf von `Ensure-Venv([hashtable]$choice)` konnte nicht binden.

## Minimalreparatur
1. winget-Prozessausgabe explizit nach `Out-Host` leiten.
2. `$LASTEXITCODE` sofort in `winget_install_exit` dokumentieren.
3. Rueckgabe `Ensure-Python` gegen Hashtables pruefen.
4. Readback-Pending nach erfolgreichem Installer-Exit getrennt von einem abgebrochenen Installer berichten.
5. Nur eine Batchdatei beibehalten. Bestehende Runtime-Module bleiben byteidentisch.

## Aktionshinweis
Wegen des vorherigen Installationsversuchs nicht erneut unbesehen Python installieren. Zuerst Diagnose (Menue 1), danach bei Bedarf Menue 2. Nur wenn Python nicht gefunden wird, bestaetigt der Nutzer die Wahl des vorhandenen Python-Pfads oder eine Installation.

## Testergebnis
`PYTHONPATH=src pytest -q`: 217 passed. Windows PowerShell 5.1 / winget nicht hier ausgefuehrt. Windows-Installations-Readback bleibt READBACK_PENDING.
