# Keyboard LED Remapper R18 — Unified Cyber Control · Integration & Audit

## Basis
- Ausgangspunkt: `KeyboardLEDRemapper-Windows-R17-CYBER-GUI-REPAIR.zip` (lokale vollständige Quelle).
- Keine Änderung an Originalarchiv, proprietären Referenz-Binärdateien, Repositories oder physischen Datenträgern.
- R18: Eine Tk-Wurzel, ein Python-Prozess, D als Standardbereich.

## Integrierte Bereiche
- D: `DriveLedWindow` im ersten Tab, bestehende R/W-Zähler und globales Lock-Mapping ausschließlich nach Opt-in.
- E: `DriveWorkspaceWindow` im zweiten Tab mit dynamischem USB-Rescan, PDH, individuellen Tray-Icons und beweglichem Overlay.
- A: Kapazitätswerte über unveränderten `VolumeSampler` im dritten Tab.
- B: klassische Oberfläche `App` im vierten Tab, weiter ohne automatischen Hardware-Modus.
- C: Windows-Tool-Manager mit ausschließlich erlaubten Aktionen Diagnose/Setup/Update/PythonRecovery; Setup und Update verlangen vorherige Zustimmung.
- Status: Übersicht über CPU, RAM, Disk, Netzwerk, erkannte Laufwerke, Tray und Overlay.
- D- und B-Bedienelemente in Scrollcontainern; E behält eigene Scroll- und Einstellungen-Container.
- Tray und Overlay bleiben jeweils separat konfigurierbar; physische HID-Schreibsteuerung bleibt OFFEN.

## Wesentliche Codeänderungen
- `src/klrw/control_center.py`: neues gemeinsames Hauptfenster mit sechs Tabs, Lifecycle und Tools.
- `src/klrw/hardware_lease.py`: gegenseitiger Ausschluss für GLOBAL Windows-Lock-Schreibzugriffe.
- `src/klrw/drive_led_window.py`: additiver `host`-Parameter, kompatibler Einzelstart, Lock-Lease.
- `src/klrw/drive_workspace_window.py`: additiver `host`-Parameter, kompatibler Einzelstart.
- `src/klrw/gui.py`: additiver `host`-Parameter, kompatibler Einzelstart, Lock-Lease.
- `START_WINDOWS_MENUE.bat`: direkte D-Startansicht bei funktionierender Umgebung, Wartungsmenü via `--menu`; A–E starten Tabs desselben Hauptsystems; D-Einzelmodus als Startfehler-Fallback.
- `tests/test_r18_unified_control_center.py`: 6 neue Vertrags- und Schutztests.

## Verifikation
- Pytest: 288 bestanden (282 Bestand + 6 neu) im Linux-Testcontainer mit PYTHONPATH=src.
- `python -m compileall -q src/klrw`: PASS.
- Echter grafischer Tk-Smoke unter `xvfb-run`: sechs Tabs sichtbar, A/E/Status aufrufbar, normaler Close ohne beobachtete Exception; **dies ist kein Windows-GUI-Test**.
- ZIP und SHA-256-Manifest: Paketprüfung und Fingerprints nach Erstellung.

## Offene Host-Abnahme
- Windows-Direktstart durch Doppelklick im R18-Starter.
- Wechsel aller sechs Tabs; D-Mapping und E-PDH/USB-Hotplug gleichzeitig unter echter Windows-GUI.
- Individuelle Tray-Icons und Overlay über normalen Exit wieder freigeben.
- Hardware-Lease durch bewusstes Opt-in und gezielte Sicherheitsabnahme; keine automatische Hardwareaktivierung.
- Manuelle Prüfung des responsiven Layouts bei 100/125/150% DPI und schmalen Fenstern.

**Status: LOCAL_TESTS_VERIFIED · WINDOWS_READBACK_PENDING · PRODUCTION_FREEZE_OFFEN.**
