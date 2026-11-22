# R13 MENU3 – Abschlussbericht

- **2026-11-21:** 204/204 Python-Tests PASS (`PYTHONPATH=src pytest -q tests`)
- **MENU2-Basis:** 199 Tests; 5 neue MENU3-Pfad-/Vertragstests.
- Bestehende Python-Projektmodule: 39/39 SHA-256-byteidentisch.
- Einziger Batch-Starter: `START_WINDOWS_MENUE.bat`.
- PowerShell unter realem Windows: `READBACK_PENDING` (hier nicht ausfuehrbar).
- Ausfuehrung von Fremd-EXE, Treiber-/Firmwarezugriff: nicht durchgefuehrt.

**Fix:** Batch `-ProjectRoot "%ROOT%"` entfernt, Root aus `$PSScriptRoot` abgeleitet. Alle Menueaktionen teilen denselben Toolmanager.
