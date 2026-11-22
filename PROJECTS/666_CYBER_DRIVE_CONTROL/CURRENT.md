# 666 CYBER DRIVE CONTROL — native project CURRENT

SYSTEM_ID: 666_CYBER_DRIVE_CONTROL
NATIVE_ROOT: PROJECTS/666_CYBER_DRIVE_CONTROL
REPOSITORY: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
BRANCH: 666MAIN_BRAIN
CURRENT_STATE: PARTIAL
ACTIVE_DEVELOPMENT: R19 Electron + Python R18 LogicalDisk/Volume API v2
R18_BASELINE: historical Windows GUI verified, 288/288 existing R18 pytest PASS locally on Linux against original r19_build sources (not yet git-imported)
R19_MAIN_PROCESS: Electron starts bridge/volume_metrics.py using Python 3.13 or KLRW_PYTHON
R19_VOLUME_PROTOCOL: cyber-drive.metrics.v2
R19_DATA_PROVENANCE: R18 Workspace volume identity and WindowsLogicalDiskSampler, if R18 source exists at r18-legacy/src or KLRW_R18_SRC
R19_SAFETY: read-only sampler; no keyboard hardware writes; no invented PDH rates; explicit SOURCE_PENDING on missing R18 source
VERIFIED_GITHUB_IMPLEMENTATION_COMMIT: 74f6dbb536300738f6878b4b7a4bca4ae0ef64bc
VERIFIED_GITHUB_TREE: 2efcf9f7293f423b78c5a32725fe6ad35c866e7a
READBACK: verified main.cjs, renderer.js, preload.cjs, volume_metrics.py, import_r18.py and bridge contract tests
TESTS: existing R18 local 288/288 PASS; Electron JS syntax parse PASS 3/3; bridge tests not executed; R19 Windows host acceptance pending
PRESERVE: existing R18 Windows project and all user selections, no replacement or deletion
OPEN_1: import entire R18 source project as native files under r18-legacy/ with hashes, run tests against exact imported revision
OPEN_2: complete D/E/A/B/C control and settings parity in Electron (present tabs are scaffolding)
OPEN_3: complete overlay hold/quiet logic + live hotplug from actual Electron instance
OPEN_4: npm dependency lock, Windows exe build, actual CPU/RAM and tray host tests
NEXT_EXECUTABLE: full R18 source migration using scripts/import_r18.py; verify original hashes and 288 tests before expanding renderer controls
NO_CROSS_SYSTEM_MERGE: TRUE
NO_FOREIGN_NATIVE_WRITES: TRUE
