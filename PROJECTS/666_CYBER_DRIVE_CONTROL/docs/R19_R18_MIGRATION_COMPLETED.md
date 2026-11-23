# R19 live R18 migration completed — build path updated

## Remote source evidence
- Original R18 ZIP SHA-256: `0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b`
- Independent source Git blob SHA1 manifest: `docs/R18_ORIGINAL_GIT_BLOBS.json` (186 distinct paths).
- Native GitHub import commit: `3e7b5f53590f5a5aaef29f098a15f929e3817297`.
- GitHub recursive tree readback: 186/186 blob SHAs match original, zero missing, zero mismatched, tree not truncated.
- Local regression on the unchanged R18 source: `288 passed in 2.29s` (Linux container, NOT Windows-host acceptance).

## One Windows build script
`START_BUILD_WINDOWS.bat` menu 9 **no longer requests a ZIP**: it checks the 186 committed Git source blobs against the immutable manifest, runs the 288-test regression, then packages portable + NSIS setup through the normal dependency/bootstrap path.

All source checks fail closed. A local clone must be updated to the new commit first. No build tools are inserted into the release UI. Hardware LED mutation remains disabled by default.

## Not yet verified
Windows build and distribution (PyInstaller sidecar; electron-builder Portable and NSIS setup with directory selection), actual Windows first launch, clean Windows host dependency check, tray/overlay/USB hotplug acceptance, final parity with R18 D/E/A/B/C. No executable or installer is claimed in this source commit.

## Next concrete action
On a Windows checkout of the verified current branch, run the one batch and menu 9 (or menu 6). Inspect BUILD/REPORTS and produced executable hashes and test them on a clean VM. Only then release/freeze.
