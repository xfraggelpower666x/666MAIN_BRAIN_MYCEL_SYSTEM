# R04 Windows Build and Functional Acceptance
The project remains one Electron desktop UI with a Python catalog engine. Source mode requires Node.js, npm and Python. Built Windows deliverables are configured to contain a PyInstaller Python bridge inside the Electron distribution.

## Developer checks
- `BUILD.cmd check`: probes installed Node/npm/Python, does not install anything.
- `npm install`: **explicit** install of Electron project dependencies. No silent systemwide upgrades.
- `py -3 -m pip install pyinstaller pypdf python-docx`: **explicit** development dependencies, only after user approval.
- `BUILD.cmd run`: test source Electron window.
- `BUILD.cmd portable` and `BUILD.cmd setup`: build separate portable and NSIS installers. `BUILD.cmd all` builds both.

The NSIS config has `oneClick=false` and `allowToChangeInstallationDirectory=true`. Portable and setup get separate names. Real Windows build and GUI user acceptance remain OPEN until verified evidence from Windows.

## User acceptance matrix
GUI boot; drag-and-drop; file picker; 100+ song split; project classification; JSON indexes; full-content clipboard copy; repeated imports; ZIP path defense; archive ZIP readback; installed EXE without system Python; installer custom directory; install/uninstall; no privacy/data loss.

## Security boundaries
No private R02 database or original backup is published. Imported files and catalog data live in the user's Electron data directory. Archive ZIP JSON indexes can be read back. Foreign system reconciliation is read-only/proposal-only.

## Limits
Python package auto detection does not imply updates or installation. The packaged Python bridge must be tested including PDF and DOCX on Windows; optional libraries are not asserted bundled until the Windows build confirms their presence.
