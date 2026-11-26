# 666 FULL LYRICS INTELLIGENCE — R06.2 A01–A03 Source Repair

Status: **SOURCE CANDIDATE / WINDOWS HOST ACCEPTANCE OPEN**.

## Provenance / recovery

- Source: `666MAIN_BRAIN` HEAD `9de79206d5946781609dffb1a9950287c320d692`
- Immutable pre-change recovery branch: `backup/full-lyrics-pre-r062-20261126-9de79206`
- R02 original data: NOT copied, edited or published
- `runtime/CURRENT.json`: intentionally NOT promoted
- Peer plugins and unrelated `PROJECTS`: unchanged

## Changes

- A01 `electron/main.cjs`: packaged bridge uses writable `userData/catalog-data` working directory rather than ASAR directory; dev mode unchanged.
- A02 `renderer/app.js`: fix clearing files after user action/import; expose accurate selected-page ARIA state and last-operation feedback. Original neon HTML/CSS and all DOM IDs preserved.
- A03 `build/BUILD_WINDOWS.ps1`: require Windows for Portable/NSIS execution, include optional pypdf/docx imports in PyInstaller, refuse unexpectedly small bridge EXE.
- Tests: `tests/test_r062_source_contract.py` (4 source-contract regressions).

## Actual local evidence

- Python public suite (R06.1 ZIP baseline + above candidate): **24/24 PASS**
- Node syntax: `electron/main.cjs`, `electron/preload.cjs`, `renderer/app.js`: **PASS**
- R02 private database test: NOT RUN — private fixture excluded
- Windows GUI / IPC integrated host / Portable EXE / NSIS Setup: **NOT RUN**
- Runtime promotion: NOT AUTHORIZED without actual host acceptance

## Remaining gates

A01 Windows electron launch + packaged Python bridge + IPC read/write + durable SQLite state.
A02 actual rendered import queue, keyboard navigation, focus, screen resizing, import workflow.
A03 reproducible Windows x64 Portable and NSIS builds, hash, first launch, editable installation folder, uninstall, data retention, no hidden paid installs.

Repository readback and final publication receipt must be verified separately after write.
