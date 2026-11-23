# R8 — Quellen-, Risiko- und Integrationsaudit

Prüfumfang: exakt 13 vom Nutzer bereitgestellte Archive, ausschließlich statische Inspektion (ZIP-/TAR-Einträge, README, Lizenz und ausgewählte Quelldateien). Es wurden keinerlei Fremdprogramme gestartet.

| Archiv | SHA-256 | Befund | Integration |
|---|---|---|---|
| `python-keyboardleds-master.zip` | `281eea8a7cd3bfd6…` | Linux ioctl/evdev LED control | Known source; R5 abstract LED kit already covers concept; no source import |
| `KBDInds_v1_0_0.zip` | `d2d24755503d4992…` | Windows executable only | Quarantined binary; not executed, no source to audit |
| `ledcapture-2.zip` | `38dd5ecd14d06154…` | Linux network packet capture LED flasher | Adapted safely as read-only interface RX/TX counters, no packet inspection |
| `cherryrgb-rs-master.zip` | `23acf86c2bbeedba…` | Rust CHERRY RGB control; per-key colors | Adapted as offline strict RGB profile validation; no hardware protocol imported |
| `cherryrgb-rs-0.2.10.zip` | `efde96012d4865e6…` | Second snapshot of cherryrgb-rs | Held as alternative source version; do not merge unverified diffs |
| `i3status-keyboard-leds-master.zip` | `82af606675951842…` | Linux i3bar status tiles | Adapted as OS-neutral status tile data model |
| `softhddi-main.zip` | `5ba2b5bf7a4c2c81…` | DOS software HDD indicator and seek sound | Historical reference only; incompatible DOS TSR and legacy keyboard controller |
| `SOFTHDDI.ZIP` | `9f1c9b60450dd0bb…` | Legacy DOS ASM + COM | Historical duplicate; binary not executed |
| `softhddi-1.13.zip` | `62269e3fa6371854…` | Versioned SOFTHDDI source | Same concept family; no DOS code imported |
| `python-keyboardleds-0.3.4.tar.gz` | `acb45b4a8e321d37…` | Historic release of Linux LED kit | Alternative version, not a new Windows backend |
| `5454557-cc954e9606d5aafa01ad0b91f8a347a5ae47e417.zip` | `e3e44b59035a3672…` | C keyboard LED source, old macOS material suspected | Source isolated; platform and license not yet fully established |
| `MonitoringDriveActivity_x64.zip` | `349c95140683a32e…` | Windows x64 EXE only | Binary quarantined and not executed |
| `DriveActivityMonitoring-MonitoringDriveActivity_x64-V1.0.1.5.zip` | `dc8be4c47894cb77…` | Windows exe distribution with CC0 README/license | Nested binary not executed; no verified Python source integration |

## Lizenz-/Quellen- und Sicherheitsgrenzen

- `cherryrgb-rs-master.zip`: MIT-Lizenz im Root-Archiv; die Hardwareprotokolle sind geräteabhängig und dürfen ohne reale Device-ID und Gerätetest nicht freigegeben werden.
- `ledcapture-2.zip`: MIT im Archiv; die originale Linux-Lösung verwendet `pyshark`, `/sys/class/leds` und Root. R8 nutzt nur psutil-Zähler.
- `python-keyboardleds-master.zip`: MIT; Linux-spezifische Gerätedateien; bereits in R5 konzeptionell berücksichtigt.
- `i3status-keyboard-leds-master.zip`: Quellheader nennt WTFPL; R8 erzeugt ein eigenes Statusmodell.
- `softhddi-*`: DOS TSR/Assembler; niemals auf Windows ausführen. Die EXE-/COM-Artefakte sind keine Grundlage für eine unabhängige Sicherheitsfreigabe.
- `KBDInds_v1_0_0.zip` und `MonitoringDriveActivity_x64.zip`: Nur ausführbare Dateien im Archiv; Herkunft und Laufzeitverhalten nicht vollständig geprüft.
- Externe Hardware-APIs, Registry, Treiber, Flash, Netzwerk-Paketmitschnitt und Services bleiben unberührt.

## Regression und Änderungen

- R7 als identische lokale Ausgangskopie (`/mnt/data/KeyboardLEDRemapper-Windows-R7`).
- Hinzugefügt: `src/klrw/network_directions.py`, `rgb_profiles.py`, `status_snapshot.py`, `sources_cli.py`, `tests/test_r8_sources.py`.
- Angepasst: `pyproject.toml` (Version und neuer CLI-Einstieg), README und R8-Dokumentation.
- Alle vorhandenen `src/klrw/*.py` aus R7 bleiben byteidentisch; keine bestehende Implementierung ersetzt.
- Auf lokalem Linux-Host durchgeführte Python-Simulation: 103 Tests PASS. Echte Windows-/CHERRY-Hardware bleibt READBACK_PENDING.
- Originalarchive wurden nicht verändert und sind nicht Teil der R8-Auslieferung.
