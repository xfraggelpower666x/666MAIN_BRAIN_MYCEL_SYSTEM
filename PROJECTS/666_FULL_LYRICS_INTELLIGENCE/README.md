# 666SOUNDsDESIGn — FULL LYRICS INTELLIGENCE

**Native project workspace on branch `666MAIN_BRAIN` — independent from MAIN BRAIN runtime authority.**

## Current state

R03 source is a locally tested Electron + Python/SQLite application. A safe GitHub migration was started here on 2026-11-22. **The complete Electron and Python R03 source has NOT yet been deposited in this repository.** This path is an active, versioned project workspace with a live project registry and continuity evidence; do not misrepresent it as a runnable GitHub checkout until source transfer and direct readback are complete.

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

Local source: `666_FULL_LYRICS_INTELLIGENCE_ELECTRON_R03_COMPLETE.zip` from this chat, containing `engine/bridge.py`, `electron/main.cjs`, `electron/preload.cjs`, `renderer/{index.html,style.css,app.js}`, `tests/test_engine.py`, `package.json`, `START.cmd`, and preserved `legacy_r02/`. Verified in current session: `python -m unittest discover -s tests -v` **10/10 PASS** on unpacked local R03.

**Not verified yet:** source-by-source GitHub migration, GitHub CI, Windows Electron host, portable EXE or installer.
