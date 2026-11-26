# R01.10.4 — Hidden startup console

## Symptom
Launching the GUI through the batch file left a PowerShell/CMD console visible behind the cyber boot and control center.

## Repair
- `STARTEN.bat` now delegates to the Windows Script Host entry `STARTEN.vbs` and exits immediately.
- `STARTEN.vbs` launches the existing `STARTEN.ps1` with `wscript.exe`-style hidden window mode (`Run` window style 0).
- The PowerShell process still uses `-NoProfile`, `-STA`, and process-scoped `-ExecutionPolicy Bypass`; no machine/user policy is changed.
- Existing cyber boot, menu, engine and explicit per-action console behavior are preserved. Action consoles remain available when an action is clicked because those actions may require approval/input and show build output.

## Acceptance boundary
Source-level regression tests and archive integrity can be checked here. Actual Windows GUI startup must still be confirmed on the user's PC.
