# R13 R14 — Archive Integration / Audit / Re-Audit

## Quelle / Scope

**Baseline:** `KeyboardLEDRemapper-Windows-R13-DYNAMIC-DRIVE-OVERLAY` (lokaler Quellstand). Kopie unter neuem Namen, keine Originalmutation. Fünf am 22.11.2026 bereitgestellte Referenzarchive separat und nur statisch untersucht. Keine Fremd-EXE ausgeführt, keine fremden Algorithmen oder Icons kopiert. Das R13-Projekt verwendet ausschließlich eigenständig geschriebene Erweiterungen.

## Referenzarchiv-Inventar

| Archiv | Beobachteter Mechanismus | Entscheidung |
|---|---|---|
| `keyboard-hddled-master.zip` | Go-Programm schaltet unter X11 eine von Caps/Num/Scroll über `xset`; Import einer GitLab-Komponente, nicht im Archiv enthalten | **Nur Referenz**, Linux-only, nicht für Windows-HID verwendet |
| `HDDLED-master-HDDLED.zip` | C# WinForms `NotifyIcon`, WMI `PhysicalDisk`, busy/idle-Bild | **Nur Referenz**, keine Geräte-/Volume-Identität, kein getrenntes R/W |
| `HDDLED-master.zip` | Überlappender C#-Quellbestand plus Solution-Dateien | **Keine doppelte Integration** |
| `disk-read-and-write-speed-master.zip` | Linux Cinnamon-Applet mit unabhängigen R/W-Raten, Einheiten, Kompakt- und Großansicht, Anzeigeintervall | **Ideen neu implementiert** in `drive_speed_display.py` und R13-Overlay; Quelle enthält GPLv2 |
| `hddledpro.zip` | `HDDLEDPRO.exe` plus `readme.txt` (Copyright HDD LED Pro, Freeware, All Rights Reserved) | **Keine Ausführung, Dekompilierung, Einbindung** der EXE; nur bisherige, separat belegte UI-Referenzen |

## Additive Erweiterungen

- `drive_speed_display.py`: unabhängige Anzeige- und Schwellenwertlogik; vier Einheiten: KiB/s, MiB/s, MB/s, bit/s, 0–3 Nachkommastellen; getrennte Lesen/Schreiben-Werte und eindeutige Kennzeichnung fehlender Messquellen.
- `drive_workspace.py`: optionale validierte persistente Einstellungen für Einheit, Dezimalstellen, Anzeigeart und Aktivitätsschwelle in bestehendem JSON-Schema 1. Alte Konfigurationen bleiben gültig.
- `drive_workspace_window.py`: Auswahllisten werden bei zahlreichen Volumes scrollbar; kompakte/detaillierte Datenanzeige, Transparenz sowie Threshold sind in der GUI einstellbar; vorhandene Tray-/Overlay- und Lock-Steuerung erhalten.
- `windows_logical_io.py`: PDH-Counter nach Entfernen eines Laufwerks freigeben und beim Reconnect neu anlegen; partielle Counter-Registrierung bereinigen. Keine Änderung der Windows-Volumes selbst.

## Geänderte / neue Dateien

- `src/klrw/drive_workspace.py`
- `src/klrw/drive_workspace_window.py`
- `src/klrw/windows_logical_io.py`
- `src/klrw/drive_speed_display.py`
- `tests/test_archive_integration_r14.py`

**Unverändert:** 42 weitere vorhandene `src/klrw/*.py` Module, bisherige Tests und Einstieg `START_WINDOWS_MENUE.bat`; ursprüngliche Dateien der Basiskopie nicht gelöscht. Standardmäßige USB-HID-Hardwareausgabe bleibt `BLOCKIERT` bis nachgewiesener Gerätetauglichkeit. Physische Windows-Lock-Zustände werden nicht ungefragt umgeschaltet.

## Verifikation

- Baseline vor Änderung: 260/260 lokale Python-Tests bestanden.
- Kandidat: **267/267 lokale Python-Tests PASS**, inklusive 7 neuer Tests zu Anzeige, Persistenz, Hotplug und Fremd-Abhängigkeits-Schutz.
- PDH-Reconnect durch Mock-Prozess geprüft, **nicht** durch echtes Windows-USB-Gerät bestätigt.
- Ein Windows-Batch-Starter im neuen Paket.
- Python-Syntaxprüfung und ZIP-CRC separat durchgeführt.

## Status

`VERIFIZIERT_LOCAL_CODE` / `READBACK_PENDING_WINDOWS` / `USB_HID_DEVICE_GATE_OFFEN`.

**Noch offen:** echte Windows-PDH-Messwerte, Hotplug am USB-Port, Scrollverhalten, tatsächliche Mehrfach-Tray-Symbole, Overlay-Positionen nach Neustart, Geräte-spezifische HID-Unterstützung, Verhalten bei Netzwerkfreigaben. Keine Produktionsfreigabe ohne Windows-Abnahme.
