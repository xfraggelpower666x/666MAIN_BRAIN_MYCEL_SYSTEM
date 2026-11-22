# R13 PythonCore Readback Repair — Audit

- **Basis:** R13-PYTHONCORE-FIX (Original unverändert)
- **B-10 / Hoch:** `TOOLS/WINDOWS_TOOL_MANAGER.ps1`, `Invoke-PythonCheck`: unverständliche Fehlschläge des bisherigen `-c`-Versionschecks. Reparatur: native `--version`-Ausführung wie vom Windows-Host erfolgreich demonstriert, Auswertung von Exitcode und Version, Fehlerhinweis im JSON-Report.
- **B-11 / Hoch:** Registry-InstallLocation zeigt realen Interpreter-Ordner, wurde nicht als direkter Kandidat übernommen. Reparatur: `Get-InstalledPythonPackages`-Orte direkt prüfen.
- **Unverändert:** Python-Anwendungsmodule, Setup-Freigaben, kein Treiberinstall, keine automatischen Deinstallationen.
- **Offen:** Windows-PowerShell-Readback und Unterstützung aller Projektabhängigkeiten unter Python 3.15.
