# R19 D/E persistence and pulse integration — November 22, 2026

## Sources and boundaries
The original R18 source tree under `r18-legacy/` is unchanged. The new `r19-electron/bridge/r19_features.py` uses R18 pure `DriveBinding/evaluate` and `BicolorActivity`. No Windows lock-state, HID or hardware-write interface was exposed.

## D
Persisted visual mappings for caps, num and scroll are stored atomically in `r19_visual_bindings.json` next to the R18 workspace file. A separate schema avoids changing R18 configuration. Valid modes: off, read, write, either. Device must be present in the R18 physical inventory. Threshold KiB/s is finite and bounded. The UI receives saved bindings and preview state; writes travel through explicit Electron main/preload IPC to Python stdin with a bounded timeout.

## E
The R18 `BicolorActivity` engine now computes an independent color for each currently present logical volume using its configured threshold, burst baseline, 180 ms hold and 450 ms quiet values (or existing saved overrides). Inactive and missing PDH samples produce OFF. E exposes volume ID, read/write, tray/overlay selection and persistent overlay layout. The overlay consumes `led_color` from R18; an 180ms client visual expiration prevents a 500ms polling interval from visually holding the LED indefinitely.

## Verification
Local original R18 source regression: 288/288 PASS.
Local D/E feature tests using R18 modules: 3/3 PASS.
New R19 tests are now also wired into the Windows build menu before freezing the sidecar; failures block packaging.
Source update and direct GitHub readback are separate from Windows host acceptance. Real Electron UI, IPC subprocess on Windows, portable and NSIS installation remain READBACK_PENDING.
