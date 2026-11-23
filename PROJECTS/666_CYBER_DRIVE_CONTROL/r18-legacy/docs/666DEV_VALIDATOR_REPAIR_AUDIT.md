# 666DEV Coding Control — Validator Repair R13

Stand: 2026-11-22. Ausgangsbasis: `KeyboardLEDRemapper-Windows-R13-PYTHONCORE-READBACK-FIX.zip` (lokaler Build, keine 666DEV-Repository-Mutation).

## Befund B-12: Falsche Python-Ablehnung

Die acht vom Benutzer bereitgestellten Windows-JSON-Berichte, insbesondere `TOOL_REPORT_20261122_024457.json`, enthalten einen Kandidaten `...\pythoncore-3.15-64\python.exe` mit `valid:false` und `execution_or_version_failed`. Der Benutzer hat denselben Interpreter in Windows PowerShell mit `Python 3.15.2` und `pip 26.2.2` erfolgreich ausgeführt. Der Fehlerbereich ist die PowerShell-Verifikation; die konkrete Ausnahmeursache ist noch nicht belegt.

## Minimalinvasiver Repair

`TOOLS/WINDOWS_TOOL_MANAGER.ps1`, Funktion `Invoke-PythonCheck`: native PowerShell-Umleitung des Python-Prozesses ersetzt durch `.NET ProcessStartInfo`, mit getrenntem stdout und stderr, Exitcode, 10s-Timeout, echter Versionsprüfung und begrenzter Fehlerprotokollierung in `python_search_notes`. Kandidatensuche, App-Module, Installation und LED-Schutzregeln bleiben unverändert. Zusätzliche fünf statische Sicherheits-/Vertragstests: `tests/test_666dev_process_validator.py`.

## Re-Audit

- Python-Regression: **243/243 PASS** (Linux-Host, Python/pytest)
- Python-Anwendungsmodule unverändert: **39/39**
- Batchdateien: **1**
- Gegenprobe mit echtem Python 3.15.2 unter Windows: **READBACK_PENDING**
- PowerShell-5.1-Parser-/Laufzeittest: **READBACK_PENDING** (kein Windows-PowerShell-Host in diesem Container)
- Feststellung `Windows PowerShell 5.1`-stderr-Mapping als mögliche Ursache: **ABGELEITET**, nicht bewiesen. Der tatsächliche Prozessfehler wird erst mit einem neuen Bericht eindeutig.

## Änderungsumfang (gegenüber Basis)

- `TOOLS/WINDOWS_TOOL_MANAGER.ps1`

## Windows-Abnahme

Vollständig entpacken, `START_WINDOWS_MENUE.bat` starten, Menüpunkt **1** und danach **2**. Bei Fehlschlag in `TOOLS/REPORTS/TOOL_REPORT_*.json` `python_search_notes` prüfen, insbesondere `exit`, `stdout`, `stderr`, `exception` bzw. `timeout`. Keine erneute systemweite Python-Installation erforderlich. Windows-Hostfreigabe erst nach Readback.
