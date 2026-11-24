# Continuity recovery delivery — PARTIAL

This is the **existing** AutoDJ Studio continuation, not a restarted application. Original `legacy/tool.ps1`, assets, bundled ffmpeg and the R05 continuity worktree are retained. R04 source Git blobs and former project Current are recorded in `docs/GITHUB_R04_SOURCE_RECOVERY_MANIFEST.json` and `history/R04_GITHUB_CURRENT.json`; **complete byte-identical R04 sources have not yet been rehydrated**. On the current shared GitHub branch the project folder is missing, so no GitHub update was attempted. Start locally with **BUILD.bat**. Windows execution remains open.

---

# 666 AUTO-DJ STUDIO — R04 CONTINUITY / R05 DELIVERY CANDIDATE

**This is a delivery candidate, NOT a new authoritative project version.** The canonical GitHub live-project remains `PROJECTS/666_AUTO_DJ_STUDIO` on `666MAIN_BRAIN` with `CURRENT.json` reporting `R04_BLOCK_RENDER_SOURCE_LIVE` at comparison time. The R05 candidate has rewritten implementations of some Electron/Python files, so file-level identity to R04 is NOT claimed. Do not replace the live branch with this ZIP.

Preserved operational source: `legacy/tool.ps1` from the historical R03 project, all available covers, and bundled FFmpeg/FFprobe binaries. The older GUI is not replaced; it can now be run directly with menu option **7**. That option copies the existing verified-by-hash bundled binaries to the path expected by original `tool.ps1`, and launches the original source unchanged. The original GUI is Windows Forms and requires Windows PowerShell.

**Run:** Extract completely, double-click the sole root `BUILD.bat`.

| Option | Action |
| --- | --- |
| 1 | Check developer tools and bundled FFmpeg |
| 2 | Prepare build dependencies (Node/Python via winget if absent) |
| 3 | Start Electron development UI |
| 4 | Build portable EXE |
| 5 | Build NSIS setup with install directory choice |
| 6 | Build both distributables |
| 7 | Start ORIGINAL preserved R03 PowerShell UI with supplied FFmpeg |

The software files under `legacy/` are historical originals and must not be silently overwritten. Node/npm/Python/PyInstaller are build-host dependencies only, never part of the normal end-user app settings. The packaged Electron deliverables are designed to include the Python interpreter and FFmpeg/FFprobe binaries. Portable EXE and setup were **not compiled on Windows in this environment**. R05 Electron functionality has not been established as identical to R04 or R03. Production freeze remains blocked.

## Canonical source references
- Repo: `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`
- Branch: `666MAIN_BRAIN`
- Path: `PROJECTS/666_AUTO_DJ_STUDIO`
- Baseline at readback: `R04_BLOCK_RENDER_SOURCE_LIVE`
- R05 differences: see `docs/RECONCILIATION_R04_R05.md`

# 666 AUTO DJ STUDIO — R05 LOCAL BUILD PACKAGE

**Windows developer build source.** Unzip anywhere, double-click **`BUILD.bat`** and choose an action. This archive is not a precompiled EXE or installer.

- **Option 3**: Prepare developer dependencies and run Electron immediately.
- **Option 4**: Create portable EXE under `dist/`.
- **Option 5**: Create NSIS installer with free target-directory selection under `dist/`.
- **Option 6**: Create both distributables.

The build requires internet for npm/Python package installation on the **builder computer**. `winget` is used to install missing Node.js and Python (no automatic system-wide upgrade of already installed versions). Electron and electron-builder are added to developer dependencies. PyInstaller bundles the Python interpreter. FFmpeg and FFprobe binaries are already included in this source ZIP and bundled into the built deliverables. The **end user's computer** should not require system Python, Node.js or FFmpeg; a real clean-Windows verification is still outstanding.

Electron neon UI is under `app/`; current isolated Python engine is under `engine/`. The original R03 `tool.ps1` and cover assets remain in `legacy/` for source-preserving migration, not silently replaced by the new engine. Legacy advanced features (cover rotation, tagging, original advanced block behavior) are **not fully ported**. Full functional parity and runtime Windows acceptance are pending. Original data is not modified; outputs use new files.

**Development status:** R05 LOCAL_BUILD_SOURCE / WINDOWS_BUILD_NOT_EXECUTED / FUNCTIONAL_PARITY_PARTIAL / NO_PRODUCTION_FREEZE.

GitHub live source: `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`, branch `666MAIN_BRAIN`, `PROJECTS/666_AUTO_DJ_STUDIO` (the included R05 candidate is a local delivery and has not been uploaded as a new GitHub commit).

## Existing AUTO-DJ R03 parity extensions (continuity candidate)
Enable **666 ORIGINAL METADATA** to write ID3 tags from `legacy/metadata.json`. Enable **ROTATE COVER POOL** to select covers cyclically; default is the preserved `legacy/covers`, or choose another folder. Enable **STREAM_READY** together with Block Mode for staged master M3U export and preservation of a prior export. Existing single-track rendering stays the default. Windows execution remains unverified. Current shared GitHub tree needs source-recovery review; this ZIP is not yet the canonical R04 export.
