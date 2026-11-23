# R12 Source and Integration Audit

## Current baseline

R11, version 1.10.0, copied without modifying existing Python modules. New version 1.11.0 adds optional tray components. No external repositories mutated.

## Sources

| Source | Verified evidence | Decision |
|---|---|---|
| AirGuanZ/KeyboardLights | GitHub main; supplied ZIP contains MIT LICENSE, KeyStateWatcher, IndicatorWindow, FullscreenDetector, TrayIconManager | Original independently designed read-only Win32 tray concept; no C# reuse or external assets |
| scj643/Keyboard_LED_status | i3-specific C++ status tool, no identified root license | Not integrated; existing snapshot APIs suffice |
| mpobrien/capslight | macOS-only native C extension, license undeclared | Not integrated |
| vimpop/tm1637-linux | Kernel module, README warns keyboard may stop accepting input | Explicitly rejected (invasive/risky) |
| justanirudh/inverto | Linux kernel USB driver modification, license undeclared | Explicitly rejected (invasive/risky) |

## New architecture

- `tray_state.py`: pure, deterministic projection of `LockSnapshot` to ordered indicator state, duplicate-suppression gate.
- `tray_window.py`: optional pystray/Pillow native Windows tray with Tk window and queue boundary for callbacks.
- `START_TRAY_WINDOWS.bat`: manual starter.
- `pyproject.toml`: optional `[tray]` dependencies, CLI entry point.

## Safety and evidence

No new hardware backend. Display is based on logical Windows lock states, not physical LED readback. No driver, firmware, registry, startup, injected key, or network mutation. Native Windows tray/fullscreen/DPI tests remain READBACK_PENDING; Linux CI tests do not establish Windows UI success.
