# 666 AUTO-DJ STUDIO — R06.1 Electron Direct Runtime Repair

Existing AUTO-DJ project only; no new identity, migration or fresh source reset.

## Source
The verified user-owned 666 FULL LYRICS INTELLIGENCE R06.1 archive includes `tools/INSTALL_ELECTRON_RUNTIME.ps1` and `tools/LAUNCH.ps1`. The recovery mechanism is adapted locally to `build/INSTALL_ELECTRON_RUNTIME.ps1`; original AutoDJ `BUILD.bat` and original PowerShell `legacy/tool.ps1` are unchanged.

## Changed
- `build/BUILD.ps1`: route missing Electron executable to the signed-manifest SHA256 verified official Electron release download, repair broken `path.txt` without re-downloading, and require literal `electron.exe` (no CRLF). The older project-local Node-22 helper remains intact but is not invoked on the new direct-download path.
- `build/INSTALL_ELECTRON_RUNTIME.ps1`: new targeted utility. Reads Electron package version, matches the AutoDJ declared dependency, downloads official Windows x64 release and manifest, verifies SHA256, extracts to temporary location, swaps into `node_modules/electron/dist`, preserves previous runtime folder and restores old path marker on failure. No global toolchain modification.

## Use
Keep the current project. Replace only `build/BUILD.ps1` and add `build/INSTALL_ELECTRON_RUNTIME.ps1`. Run `BUILD.bat`, choose `2` to prepare dependencies, then `3` to launch Electron. Internet access to github.com is needed only if the runtime is absent.

## Evidence and limitations
Static source and archive integrity checked in Linux. Real Windows 5.1 PowerShell execution, GitHub release download, developer UI launch, portable and installer builds are NOT YET VERIFIED.
