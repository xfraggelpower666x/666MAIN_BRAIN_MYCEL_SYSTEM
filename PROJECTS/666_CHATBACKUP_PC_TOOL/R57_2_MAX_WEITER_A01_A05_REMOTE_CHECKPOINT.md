# 666 CHATBACKUP PC TOOL — R57.2 · MAX WEITER A01–A05 (2026-11-26)

**Authority 1:** original 666 CHATBACKUP PC TOOL. The product branch `666MAIN_BRAIN` is NOT modified. Import Studio and Universal Buildkit remain additive, separate, preserved modules.

## Fresh local source and regression

- R57.1 full archive used as immutable reference: **391 original entries, 0 missing in R57.2**.
- R57.2 changes existing file `electron/BUILD_WINDOWS_ELECTRON.ps1` and adds `electron/verify-build-inputs.cjs`, `electron/VERIFY_WINDOWS_ARTIFACTS.ps1`, and `tests/test_electron_build_input_gate.cjs`.
- Main Python suite: **193 passed, 82 subtests passed**.
- Import Studio: **128 passed**.
- Node IPC and release-input gate tests: **4 passed**.
- Full ZIP: **396 files; SHA-256 `4d1e86182c268e7fbaf907e85ee1cae8b1de80377f146453071bc293929f263b`**; ZIP CRC PASS.
- Public-source staging: **325 content files + one transfer manifest**, SHA parity 325/325, staging SHA-256 `90bad47ac824590436cdb09e0eac29c05e2e4377c057857a15feeb68ac232d21`.
- The public staging excludes historical ZIP carriers and is **not a standalone offline release**. The earlier staging-only test result remains **190 PASS / 4 FAIL**; this has not been suppressed.

## Repair CB-A10 — release reproducibility

- `verify-build-inputs.cjs` checks actual npm lockfile/root dependency matching, installed Electron and electron-builder before running PyInstaller. The source package contains **no verified electron/package-lock.json**. A Windows release build is correctly BLOCKED until its lockfile is created/verified on a suitable host.
- `VERIFY_WINDOWS_ARTIFACTS.ps1` records actual Setup/Portable artifact SHA-256, size, fresh timestamp and build report.
- `BUILD_WINDOWS_ELECTRON.ps1` runs those gates at the proper boundaries.
- Four changed/new source files have been stored on this **candidate** branch and verified by native Git blob hashes matching the local file versions.

## Remaining gates

- **A01:** GitHub full-source transfer not complete. Direct local Git networking failed with `Could not resolve host github.com`. A Windows publisher for the prepared staging is available, with manual privacy approval and remote per-blob SHA readback.
- **A02:** Local R57.2 source/parity PASS; full remote tree SHA check still pending.
- **A03:** No real Windows Electron GUI, Studio child-process/fullscreen/settings/data persistence host evidence.
- **A04:** No real Windows Portable EXE/NSIS Setup build or installation receipt.
- **A05:** Local source FREEZE only. **NO PRODUCTION PROMOTION; no current-pointer update**.

Status: `A01 PARTIAL · A02 LOCAL VERIFIED / REMOTE PENDING · A03 HOST OPEN · A04 HOST OPEN · A05 PRODUCTION HOLD`
