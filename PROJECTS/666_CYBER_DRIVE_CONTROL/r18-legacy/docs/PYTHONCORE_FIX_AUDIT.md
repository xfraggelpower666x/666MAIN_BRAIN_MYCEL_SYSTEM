# B-09: Pythoncore-Auto-Detection · Audit → Repair → Re-Audit

- **Basis:** `KeyboardLEDRemapper-Windows-R13-REPAIR-COMPLETE`; Original-Basis unveraendert.
- **Beleg:** Nutzer hat in PowerShell unter `C:\Users\dirkm\AppData\Local\Python\pythoncore-3.15-64` `python.exe --version` erfolgreich als **Python 3.15.2** und `python.exe -m pip --version` als **pip 26.2.2** ausgefuehrt. Dennoch meldet R13 `[FEHLT]`.
- **B-09 (hoch):** `TOOLS/WINDOWS_TOOL_MANAGER.ps1`, `Find-Python`: automatische Pythoncore-Aufloesung hing von generischen/rekursiven Suchroutinen ab; es fehlte der direkte Kandidat `LOCALAPPDATA\Python\pythoncore-*\python.exe` vor der Pfadabfrage. Auswirkung: Setup blockiert trotz vorhandener, lauffaehiger Python-EXE.
- **Repair:** Direkte Auflistung aller `pythoncore-3.*`-Unterordner unter `%LOCALAPPDATA%\Python`, expliziter Kandidat `python.exe`, Versions-/Ausfuehrbarkeitstest durch das bereits bestehende `Invoke-PythonCheck`. Keine Annahme eines festen Windows-Benutzernamens; keine systemweite Installation/Mutation. Kandidaten mit Python 3.13/3.14 werden vor 3.15 bevorzugt, falls verfuegbar.
- **Geaendert:** Toolmanager, Menue-Kopfzeile, README und 4 gezielte Regressionstests. Bestehende Python-Anwendungsmodule bleiben byteidentisch.
- **Regression:** 235/235 pytest PASS auf Linux. Neues Testmodul `tests/test_windows_pythoncore_fix.py`. ZIP-Integritaet und SHA256-Manifest pruefbar.
- **Grenzen:** Windows PowerShell 5.1-Syntax/Ausfuehrung und der tatsaechliche Python-3.15-Setup-/pip-Import-Readback noch `READBACK_PENDING`. Das Windows-Protokoll bestaetigt nur Interpreter und pip, nicht die Projektkompatibilitaet.
