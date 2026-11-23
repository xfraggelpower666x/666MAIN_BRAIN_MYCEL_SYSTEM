# R19 Electron security boundaries
- nodeIntegration=false, contextIsolation=true, sandbox=true.
- renderer accesses narrow preload API only; no direct disk or shell control.
- Electron is local file-based; Content Security Policy denies outside scripts.
- Python bridge samples read-only psutil counters. No keyboard HID, drive writes or admin privileges.
- Errors are reported visibly, no fake success. Python path may be supplied via KLRW_PYTHON.
- npm dependencies are not installed by repository writes; users should review and pin dependency lock before production distribution.
- Tray icon uses a minimal built-in placeholder; design asset and Windows host check pending.
- Metrics are PHYSICAL disk counters; Windows logical volume identity is NOT mapped in this candidate.
