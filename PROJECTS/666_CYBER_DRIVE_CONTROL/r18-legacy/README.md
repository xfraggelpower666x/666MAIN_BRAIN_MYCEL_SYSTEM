# R18 — 666 CYBER DRIVE CONTROL · EIN HAUPTSYSTEM

**Normaler Windows-Doppelklick:** `START_WINDOWS_MENUE.bat` öffnet bei eingerichteter `.venv` sofort die neue R18-Oberfläche mit D als Start-Tab. Alle Bereiche A/B/C/D/E liegen in einer Anwendung; separater Status-Tab.

**Erstinstallation / Wartungsmenü:** `START_WINDOWS_MENUE.bat --menu` in CMD starten oder bei fehlender lokaler Umgebung den Batch-Starter öffnen; über [2] die vorhandene `.venv` einrichten. Die bisherigen Einzelmodule bleiben für Recovery erhalten.

**R18-CLI:** `.venv\Scripts\python.exe -m klrw.control_center --tab D`. Andere Start-Tabs: A, B, C, E, STATUS. Optional `--no-tray` und `--no-overlay`.

**Sicherheit:** USB-HID-LEDs werden nicht direkt geschrieben. Die D- und B-Hardwaremodi sind weiterhin ausdrücklich zu bestätigen und durch eine gemeinsame Hardware-Lease gegeneinander abgesichert. Nur Windows-Lock-Zustände systemweit können bei explizitem Opt-in verändert werden.

**Bekanntes Host-Gate:** Windows-GUI-/Tray-/DPI-/Hotplug-Abnahme der zusammengeführten R18 fehlt noch. Python-Tests allein sind keine Freigabe.

**Befunde und Änderungen:** `docs/R18_UNIFIED_INTEGRATION_AUDIT.md`.

---

# R14 TRAY START REPAIR

Die reparierte R14-Erweiterung erhält alle bisherigen Laufwerks- und LED-Funktionen. Neu: reproduzierbares Fehlerprotokoll und GUI-Fallback für Menüpunkt 4. Details in `docs/R14_TRAY_START_REPAIR.md`.

# R13 – Dynamischer Laufwerksmonitor / Overlay (additive Erweiterung)

**Start:** `START_WINDOWS_MENUE.bat` doppelklicken, nach erfolgtem Setup **E** wählen.

* Laufwerksliste aktualisiert sich automatisch, auch nach USB-Anschluss/Entfernung.
* **Tray** und **Overlay** separat je Laufwerk ein-/ausschalten; die zuvor vorgegebenen Buchstaben A:, B:, C:, E:, F:, X:, Y:, Z: sind beim ersten Erkennen aktiviert, USB-Tastatur bleibt aus.
* Overlay mit linker Maustaste ziehen; Position und Lock werden automatisch in `%LOCALAPPDATA%\KeyboardLEDRemapper\drive_workspace.json` gespeichert.
* Rechte Maustaste auf das Overlay blendet es aus; die Schaltfläche **Overlay zeigen** blendet es ein.
* Lesen = grün, Schreiben = rot. Native Windows-LogicalDisk-PDH-Counter werden verwendet, wo verfügbar; sonst nur exakt identifizierte `psutil`-Quellen. Bei fehlender Zuordnung steht `I/O nicht zugeordnet` statt erfundener Aktivität.
* USB-HID-Zielgeräte bleiben **nicht automatisch aktiviert**. Die ältere, separat bestätigungspflichtige **globale** Lock-Key-Steuerung ist unter D erhalten.
* Windows-Tray-Symbole, PDH und GUI erfordern noch einen tatsächlichen Windows-Hosttest.

Weitere technische Nachweise: `docs/DYNAMIC_WORKSPACE_IMPLEMENTATION.md`.

---

## NEU: Laufwerks-LED-Zuordnung

Im einzigen Windows-Menue **D** waehlen: pro Laufwerk getrennte Gruen-Lesen/Rot-Schreiben-Anzeige und optional Caps/Num/Scroll auf ein Laufwerk und dessen Aktivitaet legen. Standard: Vorschau ohne Tastatur-Eingriff. Echte Lock-Tasten-Steuerung nur nach Warnung und eigener Bestaetigung; global, nicht USB-geraeteisoliert. Siehe `docs/DRIVE_LED_MAPPING_R14.md`.

## R13 Pythoncore Fix (22.11.2026)

Siehe [README_REPAIR_START.md](README_REPAIR_START.md) fuer den reparierten Windows-Start und [docs/PYTHONCORE_FIX_AUDIT.md](docs/PYTHONCORE_FIX_AUDIT.md) fuer die Nachweise.

---

# R13 COMPLETE REPAIR

Siehe [README_REPAIR_START.md](README_REPAIR_START.md) für den aktuellen Einstieg; alle vorherigen Projektinformationen folgen unverändert.

# R13 MENU-4 — Python-Installationen wiederverwenden

**Windows-Einstieg: Nur `START_WINDOWS_MENUE.bat`.**

MENU-4 erweitert MENU-3 ohne Änderungen an den Fachmodulen. Bei Diagnose und Setup wird zuerst ein tatsächlich funktionsfähiger Python-Interpreter >=3.10 gesucht: lokale `.venv`, PATH, Python Launcher (`py -0p`), offizielle Registry-Einträge und `winget`-Paketverzeichnisse. Microsoft-Store-Aliase werden ignoriert.

**Start:** ZIP vollständig entpacken, `START_WINDOWS_MENUE.bat` doppelklicken, Punkt 1 Diagnose. Falls `NEEDS_SETUP`, Punkt 2 einmalig Setup. Eine bestehende funktionsfähige `.venv` wird nicht erneut installiert; für echte Aktualisierung Punkt 3 wählen. Eine Python-Neuinstallation über winget erfordert ausdrückliche Freigabe.

**Wichtig:** Der hier getestete Code kann nicht beweisen, wo Python auf deinem Windows-PC tatsächlich installiert ist. Wenn trotz dieser erweiterten Suche kein Interpreter gefunden wird, den JSON-Bericht `TOOLS/REPORTS/TOOL_REPORT_*.json` zur Analyse verwenden. Kein wiederholter Installationsversuch ohne neuen Befund.

**Hardware:** Kein Tastatur-LED-Schreibzugriff, keine Treiberinstallation. Native Windows-/Tray-Abnahme bleibt offen.

---

# R13 MENU3 – Windows-Quoting-Fix (21.11.2026)

**Einziger Einstieg:** `START_WINDOWS_MENUE.bat`.

**Reparatur:** Im bisherigen MENU2 wurde der Projektpfad mit einem abschliessenden Backslash als `-ProjectRoot "%ROOT%"` an PowerShell uebergeben. Unter Windows kann dadurch ein ungueltiges Anfuehrungszeichen im Argument entstehen, worauf `Resolve-Path` mit „Illegales Zeichen im Pfad“ abbricht. MENU3 uebergibt **keinen ProjectRoot-Parameter** mehr: Der PowerShell-Manager bestimmt den Projektpfad selbst aus seinem `TOOLS`-Verzeichnis. Dieser Pfad gilt damit fuer Diagnose, Installation und Update einheitlich.

**Start:** Paket entpacken, `START_WINDOWS_MENUE.bat` doppelklicken, **1** Diagnose pruefen, **2** bei fehlenden Tools installieren/reparieren (mit Freigabe), dann **4** Tray starten bzw. **7** Windows-Readback. Alle Python-Module und Funktionen aus R13 bleiben erhalten.

**Grenze:** Python-Regression hier getestet, Windows-Batch/PowerShell-Ausfuehrung auf dem Nutzer-PC weiterhin `READBACK_PENDING`. Ein fehlender Python-Interpreter wird in der Diagnose angezeigt, nicht automatisch installiert.

---

# Windows R13 - Zentrales Startmenue (Revision MENU-1)

**Einziger Batch-Einstieg: `START_WINDOWS_MENUE.bat`**. Die frueheren sieben Batch-Starter sind im neuen Lieferpaket durch diese Menue-Datei ersetzt. Die Python-Module und ihre CLI-Aufrufe sind unveraendert verfuegbar.

Menue 1 prueft Python, pip, psutil, pystray, Pillow, pytest, Windows PowerShell und optional smartctl ohne Installation. Menue 2 erstellt bei Bedarf `.venv` und installiert das Projekt mit `[tray,test]` **erst nach bewusster Auswahl**. Menues 3-9 und A starten vorhandene Funktionen; Menue 6/7 fuehren den unveraenderten fachlichen R13-Windows-Abnahmesatz aus, aber mit dem identischen Python-Interpreter wie das Menue.

**Hinweis:** Die Batch-Menueinteraktion wurde hier statisch geprueft, aber nicht unter Windows ausgefuehrt. Die Hardwareabnahme bleibt READBACK_PENDING. Zur Installation benoetigt pip gegebenenfalls Internet; kein automatisches Treiber-/Firmware-Setup.

---

# Keyboard LED Remapper — Windows Edition v1.11.0 / R12

An independent Windows implementation inspired by the idea of [Keyboard-LED-Remapper](https://github.com/suvanbanerjee/Keyboard-LED-Remapper). **Not affiliated with or endorsed by the original author.** Linux shell scripts and systemd integration are not copied. Licensed under MIT (see LICENSE).

## Requirements

- Windows 10/11 (native, for real key-state control)
- Python 3.10 or newer with tkinter (standard Windows Python installer)
- `psutil` (automatically installed by pip)
- Optional: pytest to execute tests

## Quick start (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m klrw.gui
```

Simulation CLI (safe; usable on Linux/macOS as well for testing):

```powershell
.\.venv\Scripts\python.exe -m klrw.cli --count 5
```

Explicit hardware opt-in (not recommended with actively used Caps/Num keys):

```powershell
.\.venv\Scripts\python.exe -m klrw.cli --hardware --count 10
```

Generate config and edit thresholds (percent for CPU and memory, bytes per second for other metrics):

```powershell
.\.venv\Scripts\python.exe -m klrw.cli --init-config
.\.venv\Scripts\python.exe -m klrw.cli --config klrw.json --count 5
```

**Safety:** `hardware=true` in the JSON cannot activate the hardware by itself. Hardware requires `--hardware` on CLI or explicit checkbox *and* confirmation in GUI. GUI uses default rules; JSON rules are supported by CLI. Lock-state changes are functional keyboard changes; the status LEDs cannot be independently controlled via this generic Windows method. USB/Bluetooth and OEM keyboards can ignore injected keys. Full restoration is best-effort on clean shutdown only. Sudden crashes, machine sleep, remote desktop, concurrent manual key usage or injected-key blocking can leave lock states changed. Try **Scroll Lock only** first if necessary. No administrator privileges or drivers installed by this package.

## Architecture

- `model.py`: immutable, validated metric-to-LED rules
- `config.py`: strict versioned JSON persistence with atomic replacement
- `metrics.py`: `psutil` CPU, RAM, disk I/O and network byte-rate sampler
- `engine.py`: deterministic threshold comparator; OR across shared LED targets
- `leds.py`: independent simulation backend and opt-in Windows key-state backend
- `runtime.py`: background sampler thread, cleanup and callbacks
- `cli.py`: safe-by-default headless interface
- `gui.py`: standalone Tkinter dashboard and explicit consent
- `tests/`: rule, boundary, persistence, runtime and metrics tests

## Operating principles

- No automatic startup. No scheduled task. No registry write. No driver installation.
- No telemetry. No network calls beyond `pip install` dependency download.
- No secret or configuration extraction.
- CPU/RAM are percentage measurements; I/O metrics are bytes/second (delta to previous sample).
- First sample has 0 rates because a previous counter baseline is not available.
- When multiple rules refer to a LED, any active rule activates the LED.
- Minimal input rate 0.2s; input changes only on threshold crossings.
- NOT independently addressable RGB or per-key backlight control. Needs vendor SDK and model-specific permissions.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests simulate backend state, so they do not change the real keyboard. Physical keyboard compatibility must be validated on Windows hardware separately. Never interpret a successful simulated test as proof that a physical LED responds.

## R2 (v1.1.0) — SSD-LED additive integration

Independent **conceptual** integration of [SIRprise/SSD-LED](https://github.com/SIRprise/SSD-LED) (C# Windows activity indicator) into the existing R1 Python Windows architecture; no original C# files or binaries are copied. The upstream repository does not declare a license in GitHub repository metadata; therefore no source was imported. This project retains its own MIT license.

### Combined functions

- R1 CPU/RAM/drive/network threshold rules and preview/explicit Win32 lock-key mode remain intact.
- Additional `ssd.py` adapter measures actual per-device or total disk **read/write byte-rate** using Windows-supported `psutil.disk_io_counters`. This is an I/O **rate**, not device health or SSD wear, nor proof that a physical SSD is installed.
- Color indicator: **green = reads**, **red = writes**, **yellow = simultaneous reads+writes**, **black = idle**. Intensity scales to configurable saturation in KiB/s. Visual indicator is inside the GUI (not yet a Windows tray icon).
- Choose `_total` or an OS-reported disk ID from the GUI dropdown. Identifiers come from psutil, not necessarily Windows drive letters (C: etc.).
- CLI: `py -m klrw.cli --ssd-led --count 10 --disk _total --saturation-kib 1024`
- Zero added runtime dependencies. No new drivers, registry edits, automatic startup, elevated privileges, or hardware changes for SSD monitoring.

R1 configuration format (`schema: 1`) remains unchanged. SSD indicator selection is currently session-scoped through GUI/CLI; it does **not** modify the existing JSON rules. Physical hardware LED control still requires explicit consent and may change lock key function. The upstream SSD-LED **system tray visualization is not yet implemented**; this release adds the validated read/write and per-drive indicator core.

### Testing / compatibility

`py -m pytest -q` — 20 unit/integration tests. They can run on Linux CI; real Windows 10/11 GUI/keyboard and per-disk names remain hardware acceptance checks. Python package builds from `src/` without modifying R1.

## R3 — macOS keyboard_leds conceptual adapter (additive)

The archived repository [tomohiro/homebrew-keyboard_leds](https://github.com/tomohiro/homebrew-keyboard_leds) packages a **macOS** `keyboard_leds` command through a Ruby Homebrew formula. The upstream tool supports `capslock` and `numlock` get/set, via Apple's IOKit. It does **not** provide a Windows driver, Windows keyboard-LED API or SSD monitoring. Its source code was not imported: the packaging repository has no declared license, and its formula downloads a different upstream C source.

R3 adds a **separate**, opt-in CLI command based on that interface idea:

```powershell
# Simulation only (safe default): LED get/on/off, including Scroll Lock
py -m klrw.ledctl caps get
py -m klrw.ledctl num on
py -m klrw.ledctl scroll off

# Native Windows: observe the LOCK STATE (not an independent LED signal)
py -m klrw.ledctl scroll get --hardware

# Native Windows: an explicit one-shot lock-key change (restored upon normal exit)
py -m klrw.ledctl scroll on --hardware --acknowledge-lock-change

# Advanced: leave the lock state changed intentionally
py -m klrw.ledctl scroll on --hardware --acknowledge-lock-change --keep-state
```

**Warning:** A Windows `on` operation may change the keyboard's functional Caps/Num/Scroll lock state; the LED may not respond, and normal close restores previous state unless `--keep-state` is provided. An `on` command without `--keep-state` is mainly a diagnostic transient and may barely be visible. This is **not** an independent LED driver. Every invocation starts in simulation unless `--hardware` is explicitly passed. Existing R1/R2 monitoring, SSD color indicator, GUI, and JSON schema remain unchanged.

Source evidence: `README.md`, `keyboard-leds.rb`, GitHub archived/master HEAD `a4456b266add7f797a78e5db5072a81641ff4ceb` (2017-11-23).


## R4 / v1.4.0 – virtueller Lock-Indikator

Eigenständige Windows-Implementierung der **Benutzeroberflächenidee** aus
[adrianiainlam/indicator-keyboard-led](https://github.com/adrianiainlam/indicator-keyboard-led).
Das ursprüngliche Projekt ist ein Ubuntu-/Unity-Indikator und wird nicht
installiert. Die GUI enthält jetzt eine **read-only** Anzeige für die echten
Windows-Lock-Zustände (N/C/S). Reihenfolge und Ausblendung werden über das
Anordnungsfeld gesteuert, etwa `CNS`, `NC` oder `S`.

Die Anzeige aktualisiert den Text nur bei tatsächlichen Zustandsänderungen;
die Windows-Abfrage selbst erfolgt alle 250 ms. Die Anzeige repräsentiert den
**logischen Lock-Zustand**, nicht den Zustand der physischen LED.

CLI (Preview auch außerhalb von Windows):

```powershell
py -m klrw.lockindicator_cli --preview --order CNS
py -m klrw.lockindicator_cli --order NC --json
```

Die aus dem Linux-Original bekannte Klick-Umschaltung wird bewusst **nicht**
in den read-only Indikator integriert. Für explizit freigegebene Lock-Toggles
bleibt die separate R3-`klrw.ledctl`-Schnittstelle erhalten.

Keine Dateien oder SVG-Assets aus dem Fremdprojekt kopiert. Original-README
nennt MIT für das Skript und Public Domain für SVG-Icons.


## R5 — Device-neutral LedKit (jwilk-archive/python-keyboardleds)

New module `src/klrw/ledkit.py` implements a **separate**, capability-aware
Python facade for `caps`, `num`, and `scroll`. Methods: `get()`, `set()`,
`reset()`, `toggle()`, `snapshot()`, and `set_many()`. Batch operations preserve
keys not included in the request; on a write error, rollback is attempted
(best-effort only, not a hardware transaction). All operations are simulated
by default and **never activate Windows key simulation automatically**.

Example (safe preview):

```python
from klrw.ledkit import LedKit
with LedKit() as kit:
    kit.scroll.set()
    kit.set_many({'num': True, 'caps': False})
    print(kit.snapshot())
```

Windows hardware requires `LedKit(hardware=True)` and changes *functional lock
key state*, not independent physical LEDs. This is not a hardware driver.
The source repository is archived, Linux-only, and MIT licensed; no Linux
ioctl/evdev code was copied. See `docs/R5_INTEGRATION_AUDIT.md`.


## R6 / v1.5.0 — Silakka54 RGB layer inspiration (optional preview)

The upstream [EloyEMC Silakka54 RP2040-Zero project](https://github.com/EloyEMC/Multi-color-LED-indicator-for-Silakka54-with-RP2040-Zero) demonstrates WS2812 indication with QMK layer overlays. The R6 Windows implementation is **conceptual only**: new `rgb_layers.py` priority policy and `rgb_cli.py`, isolated from the pre-existing CPU/SSD/Lock modules. **No firmware is flashed, and no physical RGB keyboard is controlled**. Real use would require device-specific, authenticated and documented HID/serial/vendor-protocol integration and explicit hardware consent.

- Layer 0: off; 1: blue; 2: green; 3: purple; Caps Lock: red with highest priority.
- Optional independent/synchronized multi-unit preview models a split keyboard without claiming any USB control.
- No EEPROM writes; no bootloader, serial or keyboard probes. The RGB policy does not change Windows lock states.
- Upstream root keymap supports independent or synchronized QMK build variants. Do not mix variants when actually flashing upstream firmware.

```powershell
py -m klrw.rgb_cli --layer 2
py -m klrw.rgb_cli --layer 3 --caps --sync
```

**License note:** GitHub describes upstream as MIT, while `config.h` contains a GPL notice. No upstream firmware code or assets have been copied. Licensing must be reviewed if firmware incorporation is proposed.


## R7 — Animationen, Auslastungsbalken und Morse (optional, Simulation)

Die bestehenden R1–R6-Dateien bleiben erhalten. Drei neue Ideen sind als
separate, selbst entwickelte Module hinzugekommen:

- `patterns.py`: endliche, deterministische Drei-LED-Animationen (`chase`,
  `bounce`, `fill`, `center`, `pulse`) und dreistufige Auslastungsbalken.
- `morse_preview.py`: internationale Morsezeichen als Zeitplan, ohne Tasten zu senden.
- `preview_scheduler.py`: Dauer-/Frame-Limits, Trennung vom Hardwarebackend.
- `animations_cli.py`: reine JSON-Vorschau, ohne `--hardware`-Schalter.

```powershell
py -m klrw.animations_cli pattern bounce
py -m klrw.animations_cli meter 67
py -m klrw.animations_cli morse SOS --led scroll
```

**Wichtig:** Animationsframes sind **keine echten LED-Steuerbefehle**. Es gibt
keine Integration in den produktiven Hardwarepfad; die Ausgabe ist eine
berechnete Vorschau. Absicht: Lock-Tasten auf Windows nicht für beliebige
Animationsfolgen umschalten, weil Caps/Num/Scroll reale Eingabefunktionen
verändern. Auch die R6-RGB-Vorschau bleibt ohne Hardwareanschluss.

### Herkunft und Lizenzentscheidung

- hexwell/kb: Windows-PowerShell-Animationen; keine ausgewiesene Lizenz.
  Nur abstraktes Animationsprinzip übernommen, kein Skript übernommen.
- Christux/KeyboardLedMonitor: Linux-Monitor mit Drei-LED-Balken und Effekten;
  GPL-2.0-or-later laut LICENSE. Unabhängige eigene Umsetzung.
- asweigart/capslockmorsecode: Morse über Lock-Tasten; GPL-3.0-or-later
  laut LICENSE. Eigenständiger Morseencoder, keine Bibliothek importiert.

Referenz-Repositories werden weder verändert noch als Abhängigkeiten eingebunden.

## R8 / v1.7.0 — Upload-Archivprüfung und sichere additive Module

Auf Basis von 13 hochgeladenen Archiven wurden drei neue, hardwarefreie Bausteine ergänzt:

- `network_directions.py`: getrennte Netzwerk-RX/TX-Messung pro Schnittstelle, mit monotonen Zählern und Schwellenwerten. **Kein Paketmitschnitt** (kein pyshark/tshark, keine Root-Rechte).
- `rgb_profiles.py`: strikte Validierung von RGB-Profileinträgen für die Vorbereitung eines künftigen optionalen CHERRY-Adapters. **Keine HID-Befehle** und keine Behauptung, dass Tastaturen kompatibel seien.
- `status_snapshot.py`: anzeigeneutrale Status-Tiles für Lock-Tasten, SSD und Netzwerk. Dies ist ein Datenmodell für ein künftiges Tray, **kein fertiges System-Tray**.
- `sources_cli.py`: nur lesende Vorschau der neuen Fähigkeiten.

```powershell
py -m klrw.sources_cli network --interface _total
py -m klrw.sources_cli locks
py -m klrw.sources_cli rgb-profile .\my-colors.json
```

Original-Dateien aus fremden Archiven wurden nicht eingebaut. Windows-EXE-Dateien wurden weder gestartet noch redistribuiert. `docs/R8_SOURCE_AUDIT.md` dokumentiert 13 Uploads sowie Lizenz- und Risikoabgrenzung.


## R9 (v1.8.0) — Disk activity desktop indicator (additive)

Standalone Windows read-only desktop widget (not a true system-tray application yet):

```powershell
py -m klrw.activity_window --disk _total --interval-ms 500
```

Alternatively run `START_ACTIVITY_WINDOWS.bat` **after installation** with `py -m pip install -e .`. The app uses Tkinter and `psutil` already required by R8; no additional packages, elevated privileges, HID writes, registry edits or device drivers. Each device measurement uses `DiskActivitySampler` from R2. The first sample is a zero baseline. Exiting closes the window; no resident service remains.

New modules: `activity_presenter.py`, `activity_window.py`, `driver_diagnostics.py`. New test file: `test_r9_activity.py`. DriverMon-style kernel monitoring is intentionally disabled until there is a separately reviewed backend.

External sources: Alezex/DiskActivityLed (proprietary binary-only, *not imported or bundled*), JovanMali/HDD-activity-indicator (WMI tray concept), helgeklein/DiskLED (performance counters; Apache 2.0), lukevella/react-activity (UI animations, MIT), Vue Interface activity indicator (URL reviewed; exact implementation not fully verified), zodiacon/DriverMon (driver diagnostics, MIT; not integrated as driver). No upstream code copied. Physical LEDs and Win32 GUI remain unverified on an actual Windows host.


## R10 (v1.9.0): SSD health / system dashboard

Die R9-Basis ist erhalten. Neue, read-only Module: `klrw.health` (optionale JSON-SMART-Abfrage ueber bereits installiertes smartctl, standardmaessig AUS), `klrw.overview` (CPU/RAM/Disk/Network-Zustand), `klrw.dashboard_window` (kombinierte Tkinter-Anzeige), `klrw.dashboard_cli` (Status als JSON).

Start: `py -m klrw.dashboard_window` oder `START_DASHBOARD_WINDOWS.bat`. JSON: `py -m klrw.dashboard_cli`. SMART bewusst und explizit anfragen: `py -m klrw.dashboard_cli --smart-device /dev/sda` (Beispielkennung; Windows-Geraetepfad je nach smartctl-Installation) (nur mit installiertem `smartctl`, Hardwareabnahme erforderlich). Die SMART-Abfrage kann je nach Hardwareberechtigungen fehlschlagen.

R10 fuehrt keine EXE aus fremden Archiven aus, installiert keine Treiber, fordert keine Administratorrechte automatisch an und schreibt keine EEPROM-/Diskdaten. Siehe `docs/R10_INTEGRATION_AUDIT.md`.


## R11 additive capacity monitoring

New independent modules: `volumes.py`, `capacity_cli.py`, `capacity_window.py`. These measure **free/used filesystem capacity**, not read/write activity or SMART device health. No remote mounts by default. Nothing is sent to a server. Missing or inaccessible mounts report limited diagnostics and do not stop other volumes.

```powershell
py -m pip install -e .
py -m klrw.capacity_cli --json
py -m klrw.capacity_window
```

Default warning thresholds: 80% used and 95% critical. Override with `--warning` and `--critical`; use `--include-remote` only when network-mounted drive capacity should be queried. `START_CAPACITY_WINDOWS.bat` launches the window after installation. The previous dashboards and LEDs are unchanged.


## R12 — Native Windows Tray (optional, read-only)

Inspired by the MIT-licensed [AirGuanZ/KeyboardLights](https://github.com/AirGuanZ/KeyboardLights), independently implemented without copying its C# code or icons. The uploaded original source ZIP was statically reviewed; it is not bundled.

```powershell
py -m pip install -e ".[tray]"
py -m klrw.tray_window
# Floating-only, no tray required (safe preview):
py -m klrw.tray_window --preview --no-tray
# Customize order (N=Num, C=Caps, S=Scroll):
py -m klrw.tray_window --order CNS
```

Native tray is available **on Windows only** and requires optional pystray/Pillow dependencies. A 3-bar status icon represents logical Caps/Num/Scroll states; updates happen only on changes and a small topmost window shows the state. Tray menu: Show/Hide, Exit. Floating window closes instead of hiding when launched with `--no-tray`. No physical LED proof, no RGB/HID writes, no startup registration, no keyboard-event injection, no registry writes, no fullscreen control or DPI guarantee. Windows-specific runtime acceptance remains OPEN pending real hardware.

Excluded Linux-only components: scj643/Keyboard_LED_status (i3), mpobrien/capslight (macOS C extension), vimpop/tm1637-linux (kernel module that can disable keyboard input), justanirudh/inverto (Linux USB keyboard driver patch). Driver manipulation was not carried over.

## R13 — Unified Windows Tray (v1.12.0)

**Einheitliches Fenster und optionales Windows-System-Tray für Caps/Num/Scroll,
Lese-/Schreibaktivität, Netzwerk RX/TX sowie RGB-Layer-Vorschau.** Die vorhandenen
Module R1–R12 bleiben erhalten. Neue Dateien:
`src/klrw/unified_state.py`, `src/klrw/unified_tray.py`,
`tests/test_r13_unified.py`, `START_UNIFIED_TRAY_WINDOWS.bat`.

```powershell
# Im entpackten Projektordner, Windows 10/11 mit Python 3.10+
py -m pip install -e ".[tray]"
py -m klrw.unified_tray
# Alternative nach Installation:
klrw-unified
# Sichere simulierte Vorschau ohne echtes Tray:
py -m klrw.unified_tray --preview --no-tray
# Andere Tastaturebene, Laufwerk, Interface und Abtastintervall:
py -m klrw.unified_tray --layer 2 --disk _total --network _total --interval-ms 500
```

- Windows-Tray: **ein Icon mit 3×3 Signalfeldern**. Reihe 1 = Num/Caps/Scroll,
  Reihe 2 = Disk Lesen/Schreiben/Netz RX, Reihe 3 = Netz TX/RGB/Neutral.
  Der Tooltip zeigt aktuelle Messwerte in KiB/s und CPU-/RAM-Prozent.
- Fenster: RGB-Layer 0–3 und Quellenkennung für Disk/NIC zur Laufzeit wählbar.
  Die Abfrage nutzt vorhandene `SystemSampler`, `DiskActivitySampler`,
  `NetworkDirectionSampler` und `WindowsLockReader`; sie erfindet keine Treiber.
- Über Tray-Menü kann das Fenster angezeigt oder verborgen und das Programm beendet werden.
  Das `--no-tray`-Fenster endet beim Schließen; es läuft nicht unsichtbar weiter.
- **Sicherheit:** kein Setzen physischer Tastatur-LEDs, keine Win32-Key-Events,
  keine Firmwareänderungen, kein Autostart/Registry-Write, kein Telemetrieversand.
- **Abnahmegrenze:** Python-Modell, Vorschau, Icon-Rendering und Tests auf Linux
  verifiziert. Echter Windows-Tray, Zustandserkennung anderer Anwendungen,
  Mehrmonitor/DPI und tatsächliche Disk-/NIC-Namenszuordnung sind auf Windows
  noch nicht abgenommen (`READBACK_PENDING`). `pystray` ist optional.
- Hinweise: Das Modell klassifiziert Aktivität anhand der gemessenen Raten, keine
  Hardware-LED-Wirkung. Windows `GetKeyState` kann je nach Eingabefokus einen
  nicht-globalen Zustand liefern; das wird bei der Hardwareabnahme geprüft.

---

## R13 MENU-2 — korrigierter Ein-Datei-Windows-Starter (21.11.2026)

**Einziger Batch-Einstieg:** `START_WINDOWS_MENUE.bat`. Die restlichen `.ps1`-Dateien sind interne Werkzeuge und keine zweiten Batch-Starter.

- **1 Diagnose:** überprüft Windows PowerShell, `winget`, eine tatsächlich startbare Python-Version **>= 3.10** (nicht nur `where python`), `pip`, virtuelle Umgebung und die Module `klrw`, `psutil`, `pystray`, `Pillow`, `pytest`. `smartctl` bleibt optional. Auch `setuptools`, `wheel` und `build` werden angezeigt (keine Laufzeitpflicht).
- **2 Installation/Reparatur:** installiert nach ausdrücklicher Zustimmung eine fehlende Python-Version über `winget` (`Python.Python.3.13`, sofern `winget` verfügbar ist), erstellt bei Bedarf **nur** eine lokale `.venv` und installiert `[tray,test]` mittels pip. Anschließender direkter Import-Readback.
- **3 Update:** installiert/aktualisiert **nach Zustimmung** pip, setuptools, wheel und Projekt-/Tray-/Testabhängigkeiten in `.venv`. Eine Python-Versionsmigration wird nicht still ausgeführt. Eine vorhandene defekte `.venv` wird niemals automatisch gelöscht.
- **4 bis B:** bestehende R13-Anwendungen, Regression und Windows-Readback; **immer dieselbe lokale `.venv`**.

Windows-App-Ausführungsaliase aus `%LOCALAPPDATA%\Microsoft\WindowsApps` gelten **nicht** als gültige Python-Installation. Ein funktionsfähiger `py`-Launcher oder eine direkt gefundene Python-Installation wird über einen wirklichen Python-Prozess geprüft. Neu installierte Versionen können auch direkt im Installationsordner entdeckt werden, selbst wenn das aktuelle Konsolen-PATH noch alt ist.

Die Tool-Diagnose und Reparatur schreibt jeweils einen JSON-Bericht nach `TOOLS/REPORTS/TOOL_REPORT_*.json`. Weder Treiber, Firmware noch Tastatur-LEDs werden im Setup verändert. `winget`/`pip` brauchen bei fehlenden Paketen Internetzugang und ggf. die systemseitige Installationsfreigabe. Falls `winget` fehlt, zeigt das Menü einen manuellen, offiziellen Python-Installationsweg, ohne einen Download zu erfinden.

**Lokale Prüfung:** Python-Regressionssuite und statische Menüsicherung. **Windows-Realbetrieb:** `READBACK_PENDING`, da hier kein Windows-Host verfügbar ist. Für einen Abnahmebericht Menüpunkt 1 und danach 2 starten; `TOOLS/REPORTS/`-JSON ist die Evidenz.


## R13 MENU-5 (Python-Wiederverwendung)

Menuepunkt 2 testet jetzt auch Python-Manager-Launcher unter WindowsApps statt diese blind zu verwerfen. Kann keine Python-Installation gefunden werden, kannst du den Pfad einer bereits vorhandenen `python.exe` manuell angeben, bevor eine Neuinstallation angeboten wird. Die automatische Suche dokumentiert getestete Kandidaten im JSON unter `TOOLS/REPORTS`. Eine vorhandene Python-Installation wird nicht aktualisiert oder ersetzt.


## MENU-6: Reparatur nach Windows-Installationsfehler

- **Fehler:** Nach `winget install` konnte PowerShell die Konsolenausgaben des Installers als Teil des Rueckgabewertes von `Ensure-Python` betrachten. Das erzeugte `System.Object[]` statt der erwarteten Hashtable.
- **Fix:** `winget` schreibt nur noch an die Konsole (`Out-Host`), der Exitcode wird sofort festgehalten und getrennt vom Interpreter-Readback protokolliert.
- **Wichtig:** Python **nicht erneut installieren**, nur weil die vorherige Sitzung `READBACK_PENDING` meldet. Im neuen Menue erst `1` Diagnose; ist Python noch nicht im PATH, `2` starten und den existierenden Python-Pfad auswaehlen.
- **Status:** Linux-basierte Python-Tests belegen keinen erfolgreichen Windows-Installationslauf. Der Windows-Readback bleibt offen.


## MENU-7: Winget meldet Python als installiert, aber nicht auffindbar
Falls `winget` das Paket `Python.Python.3.13` bereits kennt, stoppt MENU-7 automatische Wiederholungen von `winget install`. Das Tool-Inventar wird in `TOOLS/REPORTS/TOOL_REPORT_*.json` mit den Registrierungsnachweisen gesichert. Menüpunkt 2 lässt weiterhin eine vorhandene `python.exe` manuell auswählen. Eine fehlende oder defekte Windows-Installation wird **nicht** ungefragt gelöscht oder ersetzt.


## MENU-8: Windows-Python-Bestand reparieren

MENU-8 erkennt Registry-InstallPath/ExecutablePath in beiden Registry-Views, klassische Launcherpfade und zusaetzliche Paketmanager-Verzeichnisse. Alle getesteten Kandidaten und fehlgeschlagenen Pfade erscheinen im JSON unter `TOOLS/REPORTS/`. Ein `winget`-Eintrag ist kein Beweis fuer eine funktionierende EXE; bei fehlender EXE erfolgt KEIN automatisches `winget install`. Nutze nur dann die Windows-App-Reparatur (Installierte Apps -> Python -> Aendern -> Repair), wenn der Bericht bestaetigt, dass keine funktionsfaehige Python-EXE vorhanden ist. Keine automatische Deinstallation und kein Eingriff in bestehende Interpreter.

## R14 — Dynamische Anzeigen / Quellenintegration (22.11.2026)

Die erweiterte Laufwerksoberfläche (Menüpunkt E) bietet jetzt konfigurierbare R/W-Einheiten (KiB/s, MiB/s, MB/s, bit/s), 0–3 Dezimalstellen, kompakte/detaillierte Anzeige, Aktivitätsschwelle und Transparenz. Die Laufwerksliste ist scrollbar; USB-PDH-Counter werden bei Entfernen freigegeben und bei Wiederanschluss neu registriert. Bestehende Konfigurationen bleiben gültig.

Das Menü startet weiterhin mit `START_WINDOWS_MENUE.bat`; 2 richtet die `.venv` ein, E öffnet die Laufwerksverwaltung. **Kein automatischer USB-HID-Schreibzugriff.** Windows-Abnahme ausstehend.

Audit: `docs/R14_ARCHIVE_INTEGRATION_AUDIT.md`.

## R15 Cyber Neon Drive Overlay (additive Erweiterung)
- Neues Overlay-Layout in **Menuepunkt E**: `vertical` (untereinander, Namen plus I/O-Details) oder `horizontal` (nebeneinander, nur Laufwerkskuerzel und eine LED).
- **Eine LED pro Laufwerk**: Cyan = Lesen, Pink = Schreiben (Schreiben hat Prioritaet), dunkel = ruhig/nicht zugeordnet.
- Aktivitaetslogik: konfigurierbare Mindestschwelle in KiB/s, adaptiv gelernte Grundlast, konfigurierbare Impulszeit und Ruhezeit.
- Dunkelgrau/Cyan/Lila/Pink in Drive Workspace und Overlay; alle bisherigen Mess-, Tray-, Hotplug- und Tastaturfunktionen erhalten.
- **Layout** im Laufwerksfenster auswaehlen und `Anwenden` betaetigen. Fuer Impuls/Ruhe im unteren Bereich Werte auswaehlen, `Anwenden`.
- Die bereits lokal gespeicherten Laufwerksselektionen bleiben bestehen (Schema v1 und alte JSON lesbar).
- Windows-Hardwaretests weiterhin noetig; 277 lokale Python-Tests bestanden.


## R16 – Cyber Hover Minimal-Overlay

Unter **E – Dynamische Laufwerke / Tray / Desktop-Overlay** kannst du im Feld **Overlay-Layout** jetzt `vertical`, `horizontal` oder `minimal` wählen. `minimal` zeigt die Laufwerke untereinander mit nur Buchstabe und einer zweifarbigen LED. In allen drei Layouts zeigt Mouse-over den Laufwerksnamen, Status, Lese- und Schreibgeschwindigkeit, Dateisystem und die Verfügbarkeit einer Messzuordnung. `Anwenden` speichert die Auswahl.

Die vorgeschlagenen LED-Werte sind `led_hold_ms=180`, `led_quiet_ms=450` und `activity_threshold_bps=4096`; sie sind bereits R15-Standard und werden nicht ungefragt bei vorhandenen Einstellungen überschrieben.

**Readback:** 279/279 Python-Tests PASS, Windows-Overlay-Hover noch zu prüfen.
