# R9 Integration audit — 2026-11-21

## Source-specific evidence and decisions

| Source | Read evidence | Result |
|---|---|---|
| Alezex/DiskActivityLed | README.txt; LICENSE.txt | Binary-only proprietary freeware. NO import, redistribution, or reverse-engineering. Read/write visual concept only. |
| JovanMali/HDD-activity-indicator | README.md; HDDActivityIndicator.cs | Windows Forms/WMI disk monitor reference; add a standalone Tk widget using existing psutil, not C# code. License unspecified; no source copied. |
| helgeklein/DiskLED | README.md; GitHub Apache-2.0 metadata | Animated system-tray Windows performance counter reference; R9 preserves monitoring boundaries and introduces pure presentation module. Not a generic PerfCounter implementation. |
| vue-interface.github.io/packages/activity-indicator | URL | Page fetch not available; functionality NOT verified. No source imported. |
| lukevella/react-activity | README.md; MIT repo metadata | React loading animations; no React runtime added to desktop app. Frame-based presentation ideas only. |
| zodiacon/DriverMon | README.md; MIT repo metadata | Driver monitoring is not keyboard-LED activity. Capability marked disabled; no driver or elevated hook. |

## Safety and scope

R8 remains preserved as a separate directory and ZIP. R9 is an additive copy with 3 new Python modules, one BAT launcher, one test module, updated README and pyproject. No existing Python modules changed. R9 widget is a Windows Tkinter desktop window, NOT a native system tray icon. Samples are read-only; hardware LED and RGB output not activated. Negative/NaN rates rejected. Upstream binary executable not included.

## Open gates

- Windows actual display/monitor and tray acceptance: READBACK_PENDING.
- Driver ETW/performance-counter provider probe: NOT IMPLEMENTED, no automatic activation.
- Vue source-level analysis: OFFEN.
- Native hardware keyboard/RGB acceptance: READBACK_PENDING.
