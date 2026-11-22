# 666 AUTO DJ STUDIO — Live R01
Independent project in `PROJECTS/666_AUTO_DJ_STUDIO` on `666MAIN_BRAIN`.
Status: DEVELOPMENT_CANDIDATE / WINDOWS_READBACK_PENDING / NO_PRODUCTION_FREEZE.

## Direct development entry
On Windows double-click `BUILD.bat`, or `BUILD.bat run`, `BUILD.bat portable`, `BUILD.bat setup`, `BUILD.bat all`.
The builder checks and installs Node/Python (winget), npm packages, PyInstaller; builds a Python standalone EXE and bundles FFmpeg/FFprobe via electron-builder.
Build-only tools are *not* inside the end-user UI. NSIS allows an installation-directory choice. Users of compiled outputs should not need system Python, Node or FFmpeg.

**Important**: restore verified licensed FFmpeg/FFprobe binaries from original R03 under `tools/ffmpeg/` on the builder before packaging. This repo stores SOURCE, not oversized binaries. Build safely fails if they're absent.

## Architecture and preservation
Electron neon UI in `app/`; Python MP3/normalization worker in `engine/`; build tools in `build/`. Original R02 PowerShell has NOT been fully ported: Smart Shuffle, Hardcore Mix, playlists, cover rotation, metadata, detailed batch workflow remain legacy-only; preserve the original user-supplied R03 package for recovery. This live starter is NOT claimed to have complete feature parity.

No Windows GUI, portable executable, installer, audio parity or final production freeze verified.
