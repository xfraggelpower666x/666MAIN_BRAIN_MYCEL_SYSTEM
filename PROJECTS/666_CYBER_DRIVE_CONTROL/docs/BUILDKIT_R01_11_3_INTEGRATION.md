# R19 · Integration of uploaded Universal Python Electron Buildkit R01.11.3

Original evidence: user-supplied archive 666_UNIVERSAL_PYTHON_ELECTRON_BUILDKIT_R01_11_3_BUILD_MANAGER_APP_SETTINGS(2).zip; 59 entries and ZIP CRC accepted.

## Integration boundary
The original toolkit has its own control-center/ and Python HTTP backend template, and its own build/start scripts. Cyber Drive is already an Electron app with a frozen Python JSONL bridge and a proven BuildBoth Windows pipeline. The kit's template backend/packager is not wired over these native components.

## Integrated into Cyber Drive itself
- app-settings-store.cjs: whitelisted per-user fullscreen/language/theme settings; corruption safe fallback; separate from R18 data.
- isolated app-settings-preload.cjs and separate settings BrowserWindow, with strict IPC sender/frame verification.
- F11 persists fullscreen state, F10/Ctrl+, opens settings; settings button in the main UI.
- settings HTML/JS compiled as part of original Electron package through its existing package.json.
- tests/test_r19_app_settings.cjs: five source-backed regression cases, part of existing BuildBoth.
- R01.11.3-inspired WinForms Build Manager at BUILD/BUILD_MANAGER_GUI.ps1, only reachable via existing single root START_BUILD_WINDOWS.bat -> original menu option 10. This GUI invokes only BUILD_CONTROL.ps1 -Action BuildBoth and does not reimplement installation/packaging.
- full original 59-entry Buildkit source and images preserved in user-provided archive; binary artwork is NOT silently imported into live app.

## Boundaries
No change to R18 originals, no alternate Python HTTP backend, no extra root .bat, no build UI shipped in app, no system-wide tool updates without approval. Language/theme preferences are persisted but full interface language switching is not yet implemented: explicit partial parity.
Current GitHub source integration is not equivalent to Windows desktop acceptance. New CI run and artifact readback required for release acceptance.
