# 666 CYBER DRIVE CONTROL — Native Current

SYSTEM_ID: 666_CYBER_DRIVE_CONTROL
NATIVE_ROOT: PROJECTS/666_CYBER_DRIVE_CONTROL
REPOSITORY: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
BRANCH: 666MAIN_BRAIN
STATUS: PARTIAL
LAST_R18_REGRESSION: 288/288 PASS 2026-11-22 (local Linux test on original archive extraction)
SOURCE_GITHUB_MIGRATION: NOT_DONE (186 files not present in r18-legacy on remote)
PORTABLE_SETUP_WINDOWS_BUILD: NOT_EXECUTED
OPTION9_IMPORT_PATH_FIX: VERIFIED_GITHUB_SOURCE_AFTER_CORRECTION
OPTION9_FIX_COMMIT: 84e4f8589c6d7421fb1d0456ff1bea3858fb2bb5
OPTION9_FIX_TREE: e9133cf14e8232d6a68c79f5061eb065a2dcbde6
OPTION9_FIX_DETAIL: actual script parents[3] is correct checkout root, parents[2] is PROJECTS; prior change reversed
OPTION9_WINDOWS_RUN: READBACK_PENDING
REASON: Full 186-file R18 source imported and tested locally only; not yet present in this GitHub folder. Windows portable and setup executables not compiled.
R18_ORIGINAL_ARCHIVE_SHA256: 0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b
LOCAL_SOURCE_VERIFY: 186/186 original ZIP entries matched extracted bytes
LOCAL_REGRESSION: 288/288 pytest PASS on extracted R18 source (Linux environment, not Windows host)
GITHUB_MIGRATION_TOOL: scripts/R18_IMPORT_AND_VERIFY.py
GITHUB_SCOPED_PUBLISHER: scripts/PUBLISH_R18_GIT.py
GITHUB_MIGRATION_EVIDENCE: docs/R18_HOST_MIGRATION_GATE.md
GITHUB_BUILD_HOST: START_BUILD_WINDOWS.bat -> BUILD/BUILD_CONTROL.ps1
MENU_9: verify exact original ZIP; run 288 regression; import source; scoped Git commit/push; remote HEAD readback; compile portable EXE and NSIS setup
RELEASE_GATE: exact full R18 sources missing in GitHub r18-legacy/ => BUILD_BLOCKED
PREVIOUS_IMPL: R19 Electron + R18 Windows LogicalDisk metrics bridge, read-only
R19_DASHBOARD: D main; E/A/B/C navigation scaffold — full parity open
ENDUSER_RUNTIME: Electron resources plus PyInstaller frozen Python sidecar configured; actual clean-Windows runtime unverified
BUILD_TOOLCHAIN: Electron-builder portable + NSIS directory choice, PyInstaller isolated Windows build venv
HOST_TESTS: Windows build not executed; EXE installation/uninstallation and first launch READBACK_PENDING
GITHUB_READBACK: migration importer, scoped publisher, Build menu and evidence document read directly at commit 5acb69598b170ea85cad13e780863636b9212b57
PRESERVE: original R18 project; no existing code deleted
NO_FOREIGN_ACTIVATION: TRUE
NO_CROSS_SYSTEM_MERGE: TRUE
NEXT_EXECUTABLE: after updating to the repaired GitHub HEAD, from a clean Windows Git checkout on branch 666MAIN_BRAIN, run START_BUILD_WINDOWS.bat -> option 9 with the original verified R18 ZIP; inspect the remote SHA, Windows build logs, portable EXE and setup installation tests.
