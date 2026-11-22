# R19 BUILD AND PACKAGING CONTRACT — builder outside application

Single batch: `START_BUILD_WINDOWS.bat`. All tooling inside `BUILD/BUILD_CONTROL.ps1`. No build controls are injected into the Electron UI. Existing R18 legacy batch (once imported) remains untouched in `r18-legacy/`, and is not a second top-level build launcher.

## Menu
1. Detect Node >=20, npm, Python 3.13, create isolated venv, install/update pip/setuptools/wheel/psutil/PyInstaller and npm packages.
2. Run Electron in development mode with original R18 modules.
3. Freeze Python backend with PyInstaller into `r19-electron/build/engine/666CyberMetrics.exe`.
4. Package `electron-builder` Windows portable EXE.
5. Package NSIS setup EXE; **non-oneclick installer with directory selection**.
6. Both target types.
7. Directly test the most recent compiled portable EXE.
8. Status and log output.

Builder requires Windows and, for installation commands, winget plus network; if no winget, it fails with a specific error instead of silent success. If tools are already compliant, they are reused. Updates to globally installed Node/Python are NOT forced if supported versions already exist. Project dependencies are installed/updated inside build environment only. Build logs persist under BUILD/REPORTS.

## Runtime bundling
Electron bundles Chromium/Node and renderer resources. The frozen `666CyberMetrics.exe` is included via `extraResources` in portable and NSIS outputs; Python/psutil native runtime is bundled by PyInstaller. No Python/npm/node installation should be needed at end-user runtime. System DLL dependencies of a Windows-native build must be confirmed on a clean VM. FFmpeg and other third-party executables are **only** bundled when used by a supported runtime feature. There is currently no runtime FFmpeg feature; bundling it blindly wastes space and can introduce license/security concerns.

## Hard release blockers
- Original full R18 source missing => BUILD_BLOCKED; no empty Electron-shell builds.
- R18 sources must be copied into `r18-legacy` with an audited inventory. R18 source migration still OPEN.
- Offline builds require a pre-populated trusted package cache and checked-in package-lock. Until lockfile is published, generated lockfile must be committed before production freeze.
- npm/PyInstaller and PyInstaller sources undergo license/security review before production.
- Real Windows EXE, install-path selection, overlay/tray and hotplug must pass real host/clean-VM checks. GitHub publishes source only: it does not create or attest to a working Windows EXE.

## No destructive changes
No scripts in shipped application; no global system installation for end users; no silent replacement of R18, no hardware LED write, and no paid services. Build outputs and node_modules/venv excluded from git.
