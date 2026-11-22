# 666DEV R13 Readback Repair – 2026-11-22

## Basis
KeyboardLEDRemapper-Windows-R13-666DEV-VALIDATOR-REPAIR.zip; vollständige Kopie vor Reparatur in /mnt/data erhalten.

## Windows-Befund (Nutzer-Readback)
- Windows-Python 3.13.14 aus `.venv`, pip, klrw, psutil, pystray, PIL und pytest bestanden.
- Nach erfolgreichem pip-Update SyntaxError aus `python -c`: `print([OK]` – gequoteter Text wird beim Windows PowerShell 5.1-Nativaufruf verändert.
- Optionales `build` fehlt nach Tool-Update.

## Minimaländerungen
- `TOOLS/WINDOWS_TOOL_MANAGER.ps1` `Verify`: Native Python-`-c`-Prüfung verwendet nur Imports, keine eingebettete Python-Stringkonstante mehr. Erfolgsmeldung wird durch PowerShell `Note` geschrieben.
- `TOOLS/WINDOWS_TOOL_MANAGER.ps1` `Install-Dependencies`: Bei **bestätigtem** Menüpunkt-3-Update `build` gemeinsam mit pip/setuptools/wheel installieren.
- `tests/test_windows_readback_argv_fix.py`: zwei Regressionstests.
- Keine Änderungen an `src/`, keine Python-Neuinstallation, keine externen Systemwrites.

## Gegenprobe
- 245/245 Python-Tests PASS auf Linux-Host (`PYTHONPATH=src python -m pytest -q`).
- Windows PowerShell 5.1 und tatsächlicher Windows-Tool-Readback weiterhin `READBACK_PENDING`.

## Erwarteter Windows-Ablauf
Menüpunkt 3 nach Zustimmung: `pip setuptools wheel build` aktualisieren, Projekt editable aktualisieren, Import-Readback ohne Quote-SyntaxError. Menüpunkt 1 anschließend zeigt `build OK`.

## Grenzen
Weder Windows-GUI noch Hardware/Tray wurden in diesem Build-Host ausgeführt. Die vorher erfolgreichen Windows-Installationsschritte gelten ausschließlich für das vom Nutzer getestete Paket.
