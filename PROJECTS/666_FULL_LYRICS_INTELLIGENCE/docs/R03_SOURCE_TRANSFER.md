# R03 original-source migration contract

## Evidence base

This chat produced `666_FULL_LYRICS_INTELLIGENCE_ELECTRON_R03_COMPLETE.zip` (R03 local candidate). In current execution, the source directory `/mnt/data/build_lyrics_intelligence` contains Electron main/preload, renderer, Python bridge, tests, original R02 preserved as a legacy subtree, docs and one START.cmd.

## Source allowlist for public GitHub

- package.json
- START.cmd
- README.md (update to reflect GitHub state)
- engine/bridge.py
- electron/main.cjs
- electron/preload.cjs
- renderer/index.html
- renderer/style.css
- renderer/app.js
- tests/test_engine.py
- docs/ARCHITECTURE.md
- docs/AUDIT_REPAIR_FREEZE_DE.md (sanitized, no private data)

## Private / runtime exclusions

- ALL `legacy_r02/app/*.db` and `legacy_r02/reports/*.db`
- ALL `legacy_r02/exports/`, `legacy_r02/*.zip`, private lyrics files
- ALL private user imported transcripts, source backups, JSON records, archives, screenshots, secrets
- node_modules/, virtual environments, local databases, build outputs

Original R02 assets can be retained offline or via an explicitly authorized private storage path. A public repo is not their default destination.

## Migration acceptance

1. Read back the exact incoming source and compare it to original local file bytes (SHA-256 is preferred).
2. Run the existing R03 test suite from the GitHub-sourced checkout.
3. Validate Electron IPC + Python bridge endpoints and the index/database formats.
4. Confirm no sensitive data or secret files in commit diff.
5. Only then set `source_migration_status` to VERIFIED in project Current and consider build automation.

Original R03 source transfer is **READBACK_PENDING**, not silently replaced by this governance scaffold.
