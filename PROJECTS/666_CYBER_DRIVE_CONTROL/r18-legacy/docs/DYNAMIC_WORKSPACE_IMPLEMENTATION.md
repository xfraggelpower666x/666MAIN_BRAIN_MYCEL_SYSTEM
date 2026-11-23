# R13 – Dynamic Drive Workspace (additive implementation)

## What is functional
- GUI enumerates currently mounted volumes with Windows GUIDs where available and volume labels.
- Rescans at the configured interval and updates the list after hot-plug events.
- Independent persistent per-volume Tray and Overlay checkboxes. User seed A:, B:, C:, E:, F:, X:, Y:, Z: is honored as first-seen defaults; other drives default off.
- One optional pystray icon per selected available volume (Windows); no misleading aggregated counter displayed as per-volume.
- Movable desktop Toplevel overlay with recorded coordinates, position lock, and size; right click hides overlay, button reopens.
- Dual green/red I/O indicators via Windows native PDH `LogicalDisk(X:)` read/write counters where available. Falls back to exact psutil device-key match; otherwise displays `I/O nicht zugeordnet`.
- All settings stored in user-local JSON, atomic file replacement.

## Important limits / next gates
- Windows PDH `LogicalDisk(X:)` is used for per-volume rate reporting when available, independent of physical disk mapping. If PDH counters are unavailable, no physical-drive correlation is guessed.
- USB HID LED hardware is **not** controlled here. Earlier global Windows Lock-state option remains unchanged in `drive_led_window` and stays opt-in.
- Tkinter overlays and multiple tray icons have not been validated on an actual Windows GUI host.
- Volume GUID stability depends on Windows and the volume; fallback to mountpoint is not stable across letter changes.
- Reference programs (HDD LED Pro, Linux CapsLockLed, Linux diskstats, C# WMI sample) were used as design inputs, no source copied.

## Run
Windows: `START_WINDOWS_MENUE.bat` > E; or `python -m klrw.drive_workspace_window`.

## Independent USB HID interface
`src/klrw/keyboard_led_adapters.py` defines a capability contract, with fail-closed default. No USB HID transport, driver, firmware flashing or covert lock-state toggles are installed.

## Existing source preserved
Original application Python modules remain unchanged except for ADDITIVE new modules; existing Python tests only adapted where they hard-coded menu token count. No existing LED driver or sampling logic removed.
