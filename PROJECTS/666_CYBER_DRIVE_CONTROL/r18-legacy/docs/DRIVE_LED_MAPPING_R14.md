# R13 — additive Drive LED Mapping (R14 extension)

## Existing functions preserved
- `ssd.py` monitors per-drive read and write rates and already defines green=read / red=write. No file/system disk writes.
- `leds.py` already provides a WindowsLockBackend that changes **global keyboard lock key states**, not independently addressable LEDs of a particular USB keyboard.
- Prior Tray and source modules remain unchanged.

## New
- `klrw.drive_led_window` option D in the single Windows batch menu.
- Every disk from psutil per-disk counters gets **separate green read / red write** status lights, rates and progress indicators.
- Each Caps/Num/Scroll indicator can be bound to a selected drive and read/write/either/off trigger plus threshold (KiB/s).
- Pure mapping module `klrw.drive_led_mapping` testable without Windows.
- Preview by default; real lock key writes only after explicit in-app warning and confirmation. On normal close, best-effort restoration via existing WindowsLockBackend.

## Important limitation
Windows lock-key APIs change Caps/Num/Scroll functional states **globally**; there is no per-USB-keyboard isolation or physical RGB color control. USB-HID-specific LED targeting requires compatible hardware/protocol and separate permissioned implementation. This package does not install drivers or flash firmware.

## Windows acceptance open
Option 2 initializes `.venv` and option D runs the new dashboard. Check physical keyboard LEDs and changed lock states, restoration and Windows-specific behavior before production use. Neither Windows GUI nor connected USB hardware was tested in the Linux build environment.
