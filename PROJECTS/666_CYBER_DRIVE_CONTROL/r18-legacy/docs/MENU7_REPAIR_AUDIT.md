# MENU-7 Reparatur-Audit

## Input-Fehler
Windows-Rueckmeldung 2026-11-21: `winget install` meldet ein bereits vorhandenes Python.Python.3.13-Paket, kein Update vorhanden, Exit -1978335189. Die Python-EXE wurde nicht gefunden; die lokale `.venv` fehlt. Ein erneuter Installationsversuch ist nicht zielfuehrend.

## Reparatur
- Installationsinventar aus Windows-Uninstall-Registry sowie `winget list --id Python.Python.3.13` lesen.
- `InstallLocation` zur Interpreter-Suche verwenden, zusaetzliche Standardpfade pruefen.
- Bei registriertem Python ohne funktionierende EXE erneute Installation blockieren und den echten Zustand `READBACK_PENDING` melden.
- Existierende manuelle Interpreter-Auswahl und Ein-Batch-Menue beibehalten.
- JSON-Report um `installed_python_packages` und `python_search_notes` erweitern.

## Grenzen
Keine Windows-Host-Ausfuehrung in dieser Umgebung; daher kann der echte Python-Installationspfad nicht belegt werden. Windows-Registry, `winget list` und echte Hardware muessen am Host geprueft werden. Kein automatisches Deinstallieren/Reparieren systemweiter Pakete.
