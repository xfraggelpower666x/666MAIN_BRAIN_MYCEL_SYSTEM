# 666SOUNDsDESIGn — FULL LYRICS INTELLIGENCE

**Native project workspace on branch `666MAIN_BRAIN` — independent from MAIN BRAIN runtime authority.**

## Current state

R03 source is a locally tested Electron + Python/SQLite application. A safe GitHub migration was started here on 2026-11-22. **The complete public-safe R03 Electron/Python application core and regression source files have now been deposited with exact Git blob SHA parity to the local R03 version. The private original R02 data and binary backups are deliberately excluded.** This is a live, versioned source workspace. The app core is present, but read-only legacy migration requires the original private database locally; real Windows Electron host, bundled portable EXE and installer remain unverified.

- Current project state: `runtime/CURRENT.json`
- Continuity / recovery: `runtime/LIVECIRCLE.md`
- Native triggers: `runtime/TRIGGERS.md`
- Development roadmap: `runtime/NEXT_STEPS.md`
- Migration contract: `docs/R03_SOURCE_TRANSFER.md`

## Architectural contract

Electron desktop UI (neon purple, pink, cyan, charcoal) → isolated Python bridge → SQLite catalog → one JSON per record → per-project machine index → selected-record ZIP archive. Existing original FULL LYRICS TOOL V2.2 R02 remains separately preserved, with read-only optional migration.

The source repository is **public**. Keep **all real private lyrics, user backups, databases, generated catalog-data, personal transcripts, tokens, API keys and runtime archives on the user's PC**, never in this repository.

## Development continuity

All future modifications target this directory only, begin by checking the latest GitHub branch HEAD and `runtime/CURRENT.json`, and preserve history. No cross-system activation or changes to root MAIN BRAIN current. Do not silently replace R03 with a smaller rewrite.

## Local R03 baseline evidence

Local source: `666_FULL_LYRICS_INTELLIGENCE_ELECTRON_R03_COMPLETE.zip` from this chat, containing `engine/bridge.py`, `electron/main.cjs`, `electron/preload.cjs`, `renderer/{index.html,style.css,app.js}`, `tests/test_engine.py`, `package.json`, `START.cmd`, and preserved `legacy_r02/`. Verified in current session: `python -m unittest discover -s tests -v` **10/10 PASS** on unpacked local R03 with original private R02 DB. The public checkout cannot pass the legacy fixture test until the user supplies that DB offline.

**Not verified yet:** GitHub CI, Windows Electron host, portable EXE or installer. Legacy R02 migration test requires the private original R02 DB, never committed here.
