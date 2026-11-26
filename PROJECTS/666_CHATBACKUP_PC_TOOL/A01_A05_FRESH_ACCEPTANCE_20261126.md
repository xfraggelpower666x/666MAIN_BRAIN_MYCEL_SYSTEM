# 666 CHATBACKUP PC TOOL — A01–A05 fresh gate audit (2026-11-26)

Authority 1: original 666 CHATBACKUP PC TOOL. Remote location is **candidate only**; `666MAIN_BRAIN` production is not being promoted.

## A01 Publication: PARTIAL
The source staging archive contains 322 entries: 321 content entries plus the SHA-256 transfer manifest. It is prepared locally, but NOT uploaded to this repository in full. The connector can create individual text blobs, whereas direct `git ls-remote` from the local source workspace fails with `Could not resolve host: github.com`.

## A02 Source and integration: VERIFIED LOCAL / REMOTE READBACK_PENDING
Full R57.1 source archive ZIP CRC PASS; full R57.1 has zero missing files compared with R56.3. Five baseline files differ and 14 were added. The public staging omits selected binary archives/database content, and **cannot be used as a complete runtime fixture**:
- Staging-only main test: 190 passed, 4 failed, 81 subtests passed.
- Failures: missing `addons/chatback_import_studio/HISTORICAL/LEGACY_STARTERS_R01_R16.zip`, and `mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.zip` plus historical companion packages.
- These are expected absent carrier classes in the public staging, but are real failures of standalone parity; they MUST NOT be suppressed or presented as 193/193.
- Full source main tests: 193 passed, 82 subtests passed.
- Full source Import Studio: 128 passed.
- Full source Buildkit: 29 passed.
- Node IPC guard: 2 passed.

## A03 Windows Electron: READBACK_PENDING
Electron `main.js` and IPC helpers pass JS syntax / Node tests on Linux. A real Windows Electron main process, Studio child engine, fullscreen, settings and data persistence were **not executed** on a Windows host.

## A04 Portable and Setup: READBACK_PENDING
No Windows GUI, PyInstaller/NSIS host acceptance, installer execution or uninstaller test is available in this execution context. No Windows binary is asserted.

## A05 Freeze and production gate: LOCAL FREEZE ONLY
Do NOT promote current, do NOT claim GitHub full-source publication or production release until:
1. privacy-reviewed 321 staged source payload files are pushed individually into Git objects and remotely verified via blob SHA256 / exact manifest;
2. deployment-dependent backup/legacy carriers are either recovered from authorized private storage or explicitly declared external prerequisites and validated in the full-source build;
3. Windows host acceptance passes;
4. root authority and branch lease/recovery are rechecked;
5. pointer is updated **last**, only after all gates.

`A01 PARTIAL · A02 LOCAL PASS/REMOTE PENDING · A03 OPEN · A04 OPEN · A05 NO PROMOTION`
