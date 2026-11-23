# R18 exact source migration and portable/setup host build

## Local-source verification (2026-11-22)
- Original uploaded artifact: KeyboardLEDRemapper-Windows-R18-UNIFIED-CYBER-CONTROL.zip
- SHA256: `0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b`
- Archive contains exactly 186 regular files.
- Local extraction under `/mnt/data/R19_NATIVE_MIGRATION_CANDIDATE/r18-legacy/` yielded **186/186 byte-identical** original files.
- Test command on extracted local source: `PYTHONPATH=src python -m pytest -q tests`
- Result: **288 passed in 2.38 seconds**. This is an authentic local Linux regression, not Windows or Electron host acceptance.

## Actual GitHub status and one-batch path
**The 186 original source files have NOT been pushed into `r18-legacy/` in the GitHub branch by this cloud session.** GitHub Current must remain PARTIAL until direct repository readback confirms all 186 source paths.

Source import and Git publication are now reachable through one Windows batch:
`PROJECTS/666_CYBER_DRIVE_CONTROL/START_BUILD_WINDOWS.bat`
Menu **9** imports the exact source ZIP (only accepted if SHA matches), runs 288 tests, publishes only the R18 subtree through `scripts/PUBLISH_R18_GIT.py`, verifies remote HEAD, and invokes the existing `Build-Target 'both'` for Portable EXE and NSIS setup.

Necessary preconditions: a working Windows checkout on branch `666MAIN_BRAIN`, Git origin with push rights, available original R18 ZIP, network for dependency installs, and no competing branch writes during publication. A remote HEAD conflict must fail safely, not overwrite other projects. The source import/publish scripts never modify sibling folders. Build tools are developers-only; the end-user runtime carries bundled Electron and PyInstaller Python engine.

## Windows evidence requirements
- Actual Portable EXE exists, can start without installed Python/Node, and maintains tray/overlay/hotplug.
- Actual NSIS setup exists and allows choosing installation directory; uninstall succeeds.
- Confirm bundled engine, no missing Windows runtimes or DLLs on a clean Windows VM.
- Record build logs, actual EXE hashes, installation/uninstallation reports, source hashes and GitHub commit/tree/blob readback.
- No actual Windows compilation is claimed until those checks pass.

## Scope and regression
No R18 source was deleted or simplified. No other project's pointer was written. Do not promote R19 to production until feature parity and Windows execution tests are independently evidenced.
