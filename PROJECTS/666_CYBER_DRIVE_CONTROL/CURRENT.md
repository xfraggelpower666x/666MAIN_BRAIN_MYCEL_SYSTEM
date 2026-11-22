# PROJECT CURRENT — 666 CYBER DRIVE CONTROL

PROJECT_ID: 666_CYBER_DRIVE_CONTROL
NATIVE_AUTHORITY: own GitHub folder only
BRANCH: 666MAIN_BRAIN
ROOT: PROJECTS/666_CYBER_DRIVE_CONTROL
STATE: PARTIAL
CURRENT_CANDIDATE: R19 Electron Cyber HUD with read-only Python metrics bridge
R18_BASELINE: previously Windows-tested unified Tkinter application (historical 288/288 local tests), full source NOT YET IMPORTED TO THIS GITHUB FOLDER
EVIDENCE: R19 source published at commit d2eb7006bf23297728e504a3e32c8edee7dcd464
MIGRATION_TOOL: scripts/import_r18.py published at commit 800ae350ad1f9ba8e69354d89c6c18590f7d9f88
LAST_READBACK: GitHub HEAD 800ae350ad1f9ba8e69354d89c6c18590f7d9f88, direct files read successfully
SAFE_DEFAULT: hardware LED writes disabled, physical I/O counters only, no inferred Windows volume mapping
NEXT_EXECUTABLE: import original R18 source tree as normal Git files in r18-legacy; rerun regression, then wire R18 Windows PDH+volume identity, hotplug and settings into R19 Electron; Windows host test before promotion
NO_CROSS_SYSTEM_MERGE: TRUE
NO_FOREIGN_POINTER_WRITES: TRUE
