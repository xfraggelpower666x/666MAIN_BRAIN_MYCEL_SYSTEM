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

R19_DE_IMPLEMENTATION_COMMIT: 94af49b2b529b591d7bd6b5b891ac2560d3f23f9
R19_DE_IMPLEMENTATION_TREE: 1ab88678920bdcc05dd647bbcbd4b53ff0dc815c
R19_D_IMPLEMENTED: real physical DiskActivitySampler values in separate physical field, Caps/Num/Scroll visual preview only; no hardware writes, no persisted bindings yet
R19_E_IMPLEMENTED: real logical Windows PDH volumes and GUID identities, original tray/overlay state; editable tray/overlay boolean selection and minimal/horizontal/vertical layout through narrow IPC, R18 Workspace.save atomic persistence
R19_DE_UI_GUARD: editing focus preserved across 500ms metrics refresh, renderer V8 parse PASS
R19_DE_VALIDATION: remote direct readback main/preload/renderer/HTML/CSS/Python bridge; R18 unchanged original ZIP 288/288 pytest PASS on Linux
R19_DE_OPEN_TESTS: new Python command bridge IPC integration not run; Windows Electron PDH/Hotplug/Overlay/Tray visual acceptance pending
R19_DE_NEXT: execute bridge command contract tests; validate E persistence and D live-preview on Windows; implement R18 D binding persistence and E bicolor hold/quiet logic without hardening into device writes

NEXT_EXECUTABLE: Windows checkout of verified GitHub Current; START_BUILD_WINDOWS.bat -> menu 9; inspect real EXEs, setup install directory choice, tray, overlay and USB hotplug, then hash/readback release artifacts
