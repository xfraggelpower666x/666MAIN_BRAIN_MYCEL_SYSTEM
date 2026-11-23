# R19 Architecture v2 — verified source contract

## Native split
- Electron MAIN: window lifetime, tray, native overlay, narrow IPC
- Electron RENDERER: CSS/HTML Cyber HUD, display only (no nodeIntegration, no hardware writes)
- Python R18 ENGINE: `klrw.drive_workspace` discovers GUID-backed volumes and preferences; `klrw.windows_logical_io` reads PDH LogicalDisk per-letter read and write rates.
- Python volume bridge: `r19-electron/bridge/volume_metrics.py`; runs without writing keyboard state, with v2 newline JSON contract.
- Dedicated R18 full source import into `r18-legacy/` remains pending. Bridge can use `KLRW_R18_SRC` to point at verified R18 source until imported.
- Source `metrics.py` remains available as earlier physical-disk-only diagnostic fallback, but is NOT presented as volume identity.

## Protocol
Each record has `protocol: cyber-drive.metrics.v2`, `status`, `volumes` and an optional `error`. Per volume: stable `id`, letter, label, filesystem, targets, optional read_bps/write_bps and explicit measurement provenance. Absent PDH maps to `null` NOT 0. No false physical-to-logical mapping.
`settings` echoes the user-local read-only workspace: 4096B/s threshold, 180ms hold, 450ms quiet defaults; actual saved preferences take precedence.

## Security / platform
Default hardware mode OFF. No keyboard LED mutations, no admin escalation, no direct HID requests. Electron renderer remains sandboxed and isolated. Windows PDH and logical drive discovery need real Windows test. Persistent R18 JSON remains owned by the R18 engine.
UI parity for D/E/A/B/C and stable theme handling is in progress. Do not claim full native Electron production equivalence.

## Recovery
Review `CURRENT.md` before a write, validate branch HEAD/Tree and file hashes. All new code is additive. The previous Git commit is the rollback anchor. The CURRENT pointer must be updated last.
