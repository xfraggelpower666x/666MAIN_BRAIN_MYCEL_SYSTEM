# R01.11 – R06.1 Electron runtime fix and Neon Control Center

Basis: complete R01.10.5 plus the inspected Full Lyrics Intelligence R06.1 `LAUNCH.ps1`, `INSTALL_ELECTRON_RUNTIME.ps1`, `DELIVERY_R06_1.json` at MAIN BRAIN Current.

## Kept
The original full artwork, original eight-second PowerShell boot, original `electron/main.js` for the target app, Python backend engine, portable and setup, Windows WinForms fallback, historical docs and sources are unchanged unless explicitly noted.

## Added
- `control-center/`: independent fullscreen Electron GUI for tool/build menu using existing project Electron runtime. Strong sandboxed preload, fixed whitelist, user-click-only actions.
- `tools/menu-electron.ps1`: launches only if existing runtime is present, no automatic installation.
- `tools/electron-runtime-r061.ps1`: R06.1 marker repair (`path.txt` writes exactly `electron.exe` without CRLF); optional official GitHub SHA256-verified release repair after explicit permission, preserving old dist as backup.
- New `setup-control` action to install missing Electron project dependencies and repair runtime only after interactive approvals.
- Launcher now uses Electron GUI if available, WinForms fallback otherwise; logs both attempts.

## Safety
No automatic global upgrades, no background installs, no remote writes, no change to protected native system identity. Electron display may be visually superior, but actual Windows host is still READBACK_PENDING.
