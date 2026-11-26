# 666 Universal Development Buildkit — R01.11.3

## Contract / boundaries

The build manager is **development tooling**, not a component of the end-user Electron Windows application.

| Build manager | End-user Windows application |
|---|---|
| `BUILD_MANAGER.bat` -> existing `STARTEN.bat` -> hidden PowerShell start | `electron/main.js` -> BrowserWindow -> Python HTTP backend |
| Existing 8-second cyber HUD, user-cleaned original artwork | Own Electron startup splash and configured Python UI |
| Electron `control-center/` (preferred); WinForms `tools/menu-gui.ps1` fallback | No build menu, no winget, no compiler controls in package |
| `tools/bootstrap.ps1` checks tools, approves install/update, prepares Python, tests, builds | Own settings in `%APPDATA%`/Electron `userData` (per-user) |
| `tools/pack_backend.py`, electron-builder Portable/NSIS | `F11` fullscreen toggle; `F10` or `Ctrl+,` opens settings |

## Changes

- Added a separate `BUILD_MANAGER.bat` alias to the original launcher; kept `STARTEN.bat` / `STARTEN.vbs` / `STARTEN.ps1` for compatibility.
- `electron/settings-store.cjs` validates a closed schema and persists application settings in the OS user profile, with safe fallback on corrupt file and a temporary-file/rename write strategy.
- `electron/settings-preload.cjs` exposes only `load()` and `save()` to the settings window; IPC checks sender/frame in Electron main. The remote Python backend **does not** get settings IPC access.
- `electron/renderer/settings.html` and `settings.js` implement the separate settings window. Fullscreen is enabled by default; changes persist across app restarts.
- `electron/package.json` includes settings modules in the packaged application resources.
- `tools/bootstrap.ps1` keeps already installed Electron/npm dependencies and checks R06.1 runtime before Electron start/build. Missing dependencies and repairs require consent.
- Tool installation vs upgrade is explicitly selected after winget status/available-upgrade checks; no silent global upgrades.
- Portable `.exe` and NSIS setup with user-selectable install path remain the existing packaging targets.

## Limitations

- `language` and `theme` settings are saved, but the **existing Python HTTP UI must read/apply them separately**. The buildkit cannot silently modify another application's renderer/theme.
- A Windows-installed application is not validated by a Linux source check. Windows GUI startup, userData persistence under actual packaged Electron, NSIS output, and Portable behavior remain `READBACK_PENDING`.
- The pre-existing Python backend requires a local HTTP frontend and `/health` route; this is not an automatic conversion of arbitrary Tkinter, PySide, or CLI programs.
- `npm ci` on missing dependencies may refresh local node_modules as its documented behavior, only after approval. When dependencies exist, no automatic npm ci is called.
- No GitHub main-branch mutation or release promotion performed by local packaging.

## Local source regressions

- Python `python -m unittest discover -s tests -v` — 25/25 PASS.
- Node `node --test tests/settings_store.test.cjs` — 5/5 PASS.
- Node `node --check` on affected Electron/Control Center JS — PASS.

## Windows acceptance (not yet executed)

1. Double-click `BUILD_MANAGER.bat` from a directory with spaces; confirm no persistent black console, eight-second HUD, separate Control Center menu.
2. Use tool scan; try absent tool and present tool separately; verify no installation without explicit `JA`.
3. From compiler Control Center, run Python preparation/test, build Portable and NSIS setup and verify actual executable outputs.
4. Start packaged end-user Electron application; confirm fullscreen default; press `F11`; open settings with `F10` or `Ctrl+,`, save, close, restart, confirm persistence.
5. Ensure no compiler menu or privileged settings bridge is available from the backend's remote HTTP UI.
6. Carry out actual post-install test, and only then authorize production freeze.
