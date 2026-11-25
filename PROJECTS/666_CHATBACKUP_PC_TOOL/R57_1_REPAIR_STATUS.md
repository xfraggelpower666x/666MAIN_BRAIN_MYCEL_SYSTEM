# ChatBackup R57.1 — IPC Guard Re-Audit & Freeze

**Authority 1** remains the original `666 CHATBACKUP PC TOOL`. R56.3 assets, Python core, Import Studio and Buildkit are preserved by the local R57.1 candidate.

## Confirmed code finding CB-A09
In R57's Electron `main.js`, `cb:request` and `cb:pick` did not authenticate their IPC caller even though `cb:studio-open` already performed a sender check.

## Local repair
- Add `electron/ipc-guards.cjs` with main-window + main-frame identity validation.
- Wire that guard into all 3 handlers in `electron/main.js`.
- Include `ipc-guards.cjs` in the Electron `package.json` build file allowlist.
- Add `tests/test_electron_ipc_guards.cjs` covering normal and unauthorized sources.

**The new guard and test source have been uploaded to this branch. The edited main.js and package.json are NOT YET TRANSFERRED.** Do not run or promote this branch as a complete release.

## Locally observed tests
- Main Python: `193 passed, 82 subtests passed`.
- Studio: `128 passed`.
- Node IPC guard: `2 passed`.
- `node --check electron/main.js`: PASS.
- ZIP integrity: PASS.
- Real Windows Portable/Setup: PENDING.

## Next transfer gate
Transfer all **321 staged clear-source content files plus the transfer manifest**, verify GitHub blobs with local SHA-256 inventory and full remote tree before a final pointer change. Private Scriptable backups, SQLite DBs and Windows binary installer cache must not enter the public source tree.

`PARTIAL · READBACK_PENDING · NO_PRODUCTION_PROMOTION`
