# R01.11.2 — Audit, Repair and Source Freeze Candidate

## Source
Actual user-uploaded R01.11.1 ZIP (whole SHA256: ae646788d0f55ad63100628ccc67d6bd12e20a242eb11fe95163bc26bb008b1c), 49 manifest-listed original project files.

## Confirmed findings and minimal-invasive repair
- `control-center/main.cjs`: Previous launchAction returned success immediately after `spawn` invocation even if Windows emitted `error` asynchronously. Replaced with Promise resolved only on `spawn`, rejected on `error`. Renderer launch failure is now reported and exits with a non-zero code to enable original PowerShell fallback.
- `tools/electron-runtime-r061.ps1`: Existing binary-backup was already in place, but path.txt rollback lacked the original marker bytes on failed swap. Preserve and restore original marker bytes on rollback.
- `tools/publish-source-to-github.ps1`: Previous blob comparison inspected local HEAD rather than fetching the new remote HEAD. Now Git fetch + FETCH_HEAD checks, while preserving pre-change backup and no force push.
- `setup-control`: source audit **confirmed it was already fully wired in tools/bootstrap.ps1**; preserved unchanged. Earlier provisional diagnosis that this handler was absent was incorrect.

## Preserved contracts
- Eight-second static cyber boot and user-cleaned original artwork.
- Existing original Python/Electron application's electron/main.js and all build actions.
- Full-screen electron control-center, PowerShell WinForms fallback, hidden console startup.
- Per-action interactive consoles/approvals, no automatic dependency installation.
- No unrelated project changes.

## Status
SOURCE FREEZE CANDIDATE ONLY. Local regression and archive hash are executable here. Windows EXE, installer, actual WinForms/Electron host and full GitHub candidate-tree publication are not accepted until independently verified. Do not promote to production.
