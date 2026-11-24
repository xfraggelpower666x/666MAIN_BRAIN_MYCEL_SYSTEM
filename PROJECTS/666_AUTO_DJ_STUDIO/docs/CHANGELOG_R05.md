# R05 — local source package
- Exactly one root BUILD.bat; build internals moved to build/BUILD.ps1.
- Source contains Electron UI, Python worker, M3U, block planning and the existing R03 legacy code and covers for incremental migration.
- Vendor FFmpeg/FFprobe Windows EXEs from provided R03 source archive are bundled into ZIP, and configured for packaging into portable and setup outputs.
- Node.js/Python installation, Python engine executable build, Electron portable/NSIS packaging under BUILD.bat, not inside end-user UI.
- No Windows portable EXE, NSIS installer or full original audio parity is claimed as verified.
