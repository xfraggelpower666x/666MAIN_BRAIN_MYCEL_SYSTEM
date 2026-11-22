# 666 CYBER DRIVE CONTROL — Native Current

SYSTEM_ID: 666_CYBER_DRIVE_CONTROL
PROJECT_ROOT: PROJECTS/666_CYBER_DRIVE_CONTROL
REPOSITORY: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
BRANCH: 666MAIN_BRAIN
STATUS: PARTIAL
CURRENT_CANDIDATE: R19 Electron + Python R18 metrics bridge + Windows build and packaging toolchain
IMPLEMENTATION_COMMIT: ef21abd55651c17c2b53d68e8e480ac7e1ce4473
IMPLEMENTATION_TREE: 0c7da2b6d70dbb71c41fd2eed8d5300411cc91cf
BUILD_STARTER: START_BUILD_WINDOWS.bat (one top-level batch)
BUILD_CONTROL: BUILD/BUILD_CONTROL.ps1 (developer-side only)
PACKAGING: electron-builder 25.1.8 (portable / NSIS), PyInstaller Python frozen sidecar
INSTALLER_MODE: oneClick=false, allowToChangeInstallationDirectory=true
RUNTIME: Electron bundled Chromium/Node; Python sidecar frozen and included via extraResources; system dependencies subject to clean-Windows verification
BUILD_ACTIONS: prerequisite check/repair, development start, engine freeze, portable EXE, setup EXE, both, direct portable test
RELEASE_GATE: source original full R18 under r18-legacy/ MISSING => BUILD_BLOCKED
APP_SCOPE: BUILD tools not included in shipped app
CODE_READBACK: HEAD + BAT + PowerShell + package.json + Electron main + Python bridge read back; JS syntax parsed
TESTS: R18 prior 288/288 local; R19 Windows portable/setup execution NOT RUN; PowerShell runtime syntax NOT RUN; no binaries claimed
OPEN: migrate full R18 files; publish verified package-lock; test compiled app in clean Windows VM; test installer selected path and bundled dependencies; E/A/B/C parity
NO_CROSS_SYSTEM_MERGE: TRUE
NO_FOREIGN_WRITES: TRUE
NEXT: import R18 complete source as Git files with SHA-256, run baseline tests on imported tree, then Windows compile and host acceptance
