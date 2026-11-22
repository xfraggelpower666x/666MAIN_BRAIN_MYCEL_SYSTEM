# R7 Integrationsaudit — 2026-11-21

## Quellen / Readback

| Repository | Quellen | Lizenz | Übertragene Idee |
|---|---|---|---|
| https://github.com/hexwell/kb | README.md, kb.ps1 | Keine LICENSE sichtbar | Animationen als endliche Framefolgen |
| https://github.com/Christux/KeyboardLedMonitor | README.md, klm.h, LICENSE, morse.h | GPL-2.0-or-later | LED-Auslastungsbalken und Moduskonzept |
| https://github.com/asweigart/capslockmorsecode | README.md, LICENSE | GPL-3.0-or-later | Morse-Zeitplan |

## Änderung

Neue Dateien: `src/klrw/patterns.py`, `morse_preview.py`, `preview_scheduler.py`, `animations_cli.py`, `tests/test_r7_patterns.py`.
Ergänzt: `pyproject.toml` (v1.6.0 und CLI Entry Point), README.
Alle vorherigen `src/klrw`-Dateien unverändert.

## Sicherheitsgrenzen

- Keine Kopie von GPL- oder unlizenzierter Originalimplementierung.
- Kein Win32-Key-Event, kein LED-Treiber, kein USB, kein Firmwareflash aus R7.
- Keine automatische Aktivierung oder paralleler Hardwarepfad.
- Bounded Frames und Laufzeiten; Preview-Ausgabe ausschließlich JSON.
- Keine Garantie von tatsächlicher Windows-Hardwarekompatibilität.

## Open

Windows 10/11 realer Test, System-Tray, priorisierte Hardwarearbiter-Integration,
geräteabhängige RGB-Adapter und messbarer End-to-End-Readback.
