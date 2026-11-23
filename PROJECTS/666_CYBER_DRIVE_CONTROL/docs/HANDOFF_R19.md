# Handoff R19 — interrupted work recovery

Project: 666 CYBER DRIVE CONTROL
Target: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM / 666MAIN_BRAIN / PROJECTS/666_CYBER_DRIVE_CONTROL
Confirmed context: R18 D-core unified GUI boots on Windows; user confirmed A/B/C/D/E work, USB-HDD attach detection, overlay and tray. Prior local R18 regression reported 288/288 PASS; that is historical context and is not a fresh GitHub or Windows acceptance of this R19 candidate.

R19 desired: Electron front end with cyan/pink/purple/graphite palette; D default; E drive workspace; compact horizontal or vertical overlay, single read/write dual-color LED, mouseover volume details; LED 180ms, quiet 450ms, threshold 4096B/s; optional keyboard LEDs off by default; portable Windows setup.

This first repository publish provides real R19 source and read-only native Python sample bridge. Unfinished scope is **tracked rather than misrepresented as done**:
- Full R18 source: migration pending (historical original archive available in conversation, not yet uploaded into repo).
- Electron runtime not executed in Windows yet.
- Python backend uses psutil physical disk counters; no false per-volume mapping.
- Visual parity with R18, persistence, hotplug, USB-specific HID, build and packaging pending.

Recovery: inspect CURRENT.md, git branch HEAD, and this handoff; compare current files before continuing. Never promote backup/history to live without readback. Immutable pre-change git commit is the backup of parent repository state.
