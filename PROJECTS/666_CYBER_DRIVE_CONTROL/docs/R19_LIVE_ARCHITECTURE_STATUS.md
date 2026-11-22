# R19 LIVE ARCHITECTURE — DEVELOPMENT CONTROL

## Completed (repository source)
- One independent project root in PROJECTS, with GitHub Current and Handoff.
- Electron frontend (one window, D default, E/A/B/C/system tabs as navigation placeholders, isolated renderer).
- Python metrics v2 reads R18 real source when provided via KLRW_R18_SRC or imported r18-legacy/src.
- Windows LogicalDisk read/write counters and stable volume identity from R18 modules.
- Saved visibility and overlay defaults are read from R18 Workspace; no destructive cross-system mutation.
- Error and SOURCE_PENDING states are exposed instead of fake live data.
- Read-only versioned newline JSON contract; no HID hardware writing.
- R18 source import tool with SHA-256 inventory and no automatic Git publication.

## Still open (do not label as complete)
- Actual full 186-file R18 import as ordinary Git files.
- Rendering and persistence of all D/E/A/B/C settings in Electron (tabs currently navigation scaffolding).
- Real Windows Electron host launch, installer/EXE packaging and tray icon quality.
- Hardware-specific USB keyboard LED capability tests and explicit consent.
- Live USB unplug/replug in Electron and standalone overlay hold/quiet timing parity.
- Electron host resource comparison versus working Tkinter R18.

## Gates for completion
1. Import complete R18 source and verify SHA-256 inventory against original archive.
2. Run all 288 baseline tests from the imported git tree, not merely prior local copy.
3. Run Python bridge contract tests and Node static checks against the exact git revision.
4. Test Windows PDH, USB attach/detach, overlay and tray from one Electron process.
5. Only then mark R19 production-ready after host readback.

## Evidence
Previous R18 local source in working container: `PYTHONPATH=src python -m pytest -q tests` — 288 passed in 2.45 seconds, Linux environment, **not** production Windows proof.
R19 GitHub files were directly reread after publication; Node/Electron runtime not yet executed.
