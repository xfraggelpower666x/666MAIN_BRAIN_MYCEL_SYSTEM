# R13 INTEGRATION AUDIT — Unified Windows Tray

## Ziel und Basis

Ausgangsstand: lokal vorhandenes R12 v1.11.0 (170 Tests). R13 ist eine Kopie,
keine Überschreibung. Die bestehenden Python-Quelldateien wurden byteidentisch
beibehalten, ausgenommen projektweite Metadaten (`pyproject.toml`) und die additive README.

## Einbindung

| Quelle R12 | Verwendung R13 | Grenze |
|---|---|---|
| `lock_indicator.py` | `LockSnapshot`, `WindowsLockReader` | logischer Lock-Status, keine Hardwaregarantie |
| `ssd.py` | `DiskActivitySampler`, `DiskRates` | I/O-Raten, keine SMART-Diagnose |
| `network_directions.py` | `NetworkDirectionSampler`, `NetworkRates` | Schnittstellenzähler, kein Packet Capture |
| `metrics.py` | `SystemSampler` | CPU-/RAM-Werte |
| `rgb_layers.py` | `RGBPolicy` | reine Farb-Vorschau, kein HID |
| `status_snapshot.py` | Statuskacheln und Aktivitätsflags | Präsentationsmodell |
| `tray_window.py` | bleibt eigenständig nutzbar | nicht ersetzt |

Neue Architektur: `UnifiedSampler → compose_frame → UnifiedFrame → Tk/pystray`.
Tk besitzt den UI-Thread; pystray-Menüaktionen werden nur in eine Queue geschrieben.
Über den Tray wird ein einziges Icon gerendert. Es gibt keinen automatischen
Autostart, keine Treiberinstallation, keine USB-/RGB-Firmware-Schreiboperation.

## Fehlerbehebung während Entwicklung

Test `test_change_fingerprint` entdeckte, dass `layer` bei aktivem Caps Lock
im Änderungsfingerprint fehlte. Ergänzt; nach Wiederholung 187/187 PASS.

## Restlücken

- Native Windows 10/11 Start-/Stop-/Hide-/Show-Abnahme und optionales `pystray` nicht getestet.
- GetKeyState-Fokus-Verhalten und Symbol-/Tooltip-Aktualisierung auf echter Taskbar offen.
- RGB steuert ausschließlich Vorschau, nicht reale LEDs.
- Physikalische Gerätezuordnung für psutil-Perdisk- und Windows-Laufwerksnamen kann abweichen.
- Der R13-Monitor zeigt keine SMART-Warnungen oder freie Laufwerkskapazität im Icon;
  deren R10-/R11-Module bleiben separat vollständig erhalten.

Status: `VERIFIZIERT_LOCAL_PYTHON` / `READBACK_PENDING_NATIVE_WINDOWS`.
