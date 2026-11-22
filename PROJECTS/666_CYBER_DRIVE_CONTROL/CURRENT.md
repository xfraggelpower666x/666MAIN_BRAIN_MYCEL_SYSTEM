# 666 CYBER DRIVE CONTROL — Native Current

SYSTEM_ID: 666_CYBER_DRIVE_CONTROL
REPOSITORY: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
BRANCH: 666MAIN_BRAIN
NATIVE_ROOT: PROJECTS/666_CYBER_DRIVE_CONTROL
STATE: PARTIAL (source migration VERIFIED, Windows build and R19 feature parity pending)
R18_FULL_SOURCE: VERIFIED_GITHUB
R18_PATH: PROJECTS/666_CYBER_DRIVE_CONTROL/r18-legacy/
R18_FILE_COUNT: 186
R18_GIT_MIGRATION_COMMIT: 3e7b5f53590f5a5aaef29f098a15f929e3817297
R18_ORIGINAL_ZIP_SHA256: 0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b
R18_ORIGINAL_GIT_BLOBS: docs/R18_ORIGINAL_GIT_BLOBS.json
GITHUB_READBACK: 186/186 original blob SHAs match; 0 missing, 0 mismatched; recursive Git tree not truncated
R18_LOCAL_TESTS: 288/288 PASS (2026-11-22, Linux container on unchanged original source)
BUILD_IMPLEMENTATION_COMMIT: 19105d6a226efa243ed11efe4f10ec85eccab79e
BUILD_START: START_BUILD_WINDOWS.bat -> BUILD/BUILD_CONTROL.ps1
BUILD_MENU9: no ZIP required; verify committed 186 R18 files, run 288 regressions, freeze Python sidecar, package portable and NSIS setup
BUILD_SOURCE_VERIFIER: scripts/VERIFY_R18_RELEASE.py
BUILD_OUTPUTS: Windows Portable EXE and NSIS Setup are CONFIGURED, NOT BUILT
WINDOWS_HOST_EXECUTION: READBACK_PENDING
R19_ELECTRON_UI: D default, remaining tab parity still PARTIAL
RUNTIME_BUNDLE: Electron and frozen Python engine configured, clean-Windows verification OPEN
PRESERVE: original R18 code, versions, tests, Windows launchers retained under r18-legacy
SCOPE: no foreign systems changed; no Git force; no backup promoted to live
NEXT_EXECUTABLE: Windows checkout of verified GitHub Current; START_BUILD_WINDOWS.bat -> menu 9; inspect real EXEs, setup install directory choice, tray, overlay and USB hotplug, then hash/readback release artifacts
