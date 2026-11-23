# R19 DEEP AUDIT / DEEP REPAIR — Windows CI evidence, 2026-11-23

## Authority and scope
Native repository xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM, branch 666MAIN_BRAIN. Cyber Drive project only; R18 original 186-file source and R19 UI unchanged. LYVRA CODING PROFI coordinates technical implementation; foreign native owners retain authority.

## Causal source findings
- Existing BUILD/BUILD_CONTROL.ps1 had interactive Read-Host only. It could not be directly used by a headless Windows CI runner.
- No .github/workflows/cyber-drive-r19-windows.yml existed. A 666StreamTranscoder workflow is unrelated and must remain separate.
- Build-Target previously logged a dist path without verifying two actual Windows artifacts or a frozen Python-sidecar sample.
- npm package-lock.json is not committed; dependency reproducibility remains partial.

## Minimal source changes
1. BUILD/BUILD_CONTROL.ps1 now accepts optional -Action BuildBoth, preserving Menu and the unchanged START_BUILD_WINDOWS.bat.
2. BuildBoth follows the existing R18 source verification and regressions, R19 Node/Python test gates, Python sidecar freeze, smoke --once, electron-builder portable+NSIS and SHA256/size checks on expected EXE files.
3. Dedicated Windows 2022 GitHub Actions workflow builds from the checked-out commit and uploads only evidence/logs and distributable artifacts. Its workflow does not install tools into Electron and does not modify other projects.

## Actual host evidence
Run 45243219352 (c7eb031297f115518d7a03aab8d9e602877b02b4): FAILED. Windows runner completed checkout, setup-node and setup-python; Node version query sent malformed JavaScript `process.versions.node.split(.)[0]` from Windows PowerShell. This caused an incorrect winget fallback, which is absent on the runner. This is an observed cause, not a hypothetical CI environment issue.
Repair commit 934276e2efc27b75c4d495285b1199f51753dc53 replaces the fragile node -p quoting with a validated `node --version` regex.
Run 45243406158 (934276e2efc27b75c4d495285b1199f51753dc53) started automatically; as of the documented readback, original Windows build controller was in progress. Do not infer success or EXE output from a running job.

## Acceptance still required
- Result and logs of run 45243406158.
- Independent GitHub artifacts readback; confirm exactly one Portable and one NSIS Setup EXE, sizes, SHA256, PE signatures and release source commit.
- Real Windows GUI startup, overlay, tray, USB hotplug and install-directory-picker UX, beyond CI binary existence.
- Stable npm dependency lockfile. Not silently replaced by generated CI files.

Status: PARTIAL / WINDOWS BUILD READBACK_PENDING until runtime receipts exist.
