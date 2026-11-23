# 666 CYBER DRIVE CONTROL — native live project

Independent project at `PROJECTS/666_CYBER_DRIVE_CONTROL` on branch `666MAIN_BRAIN`.
Project owner: 666SOUNDsDESIGn. No foreign native-system activation.

## Project state
- R18: Windows-tested unified Tkinter application (D primary, A/B/C/E retained). **Full original source migration is still pending**. Do not infer that the Electron prototype replaces it.
- R19: additive, independent Electron Cyber HUD candidate with an isolated read-only Python metrics bridge. Caps/Num/Scroll hardware writes are intentionally unsupported.
- Source authority for this project: this own folder and its CURRENT.md; no 666TDH, 666CLS, LYVRA, CLIC or MAIN BRAIN identity or pointers are changed.
- Current native state: PARTIAL — project initialized and R19 candidate source published; R18 full migration, live Windows Electron host acceptance and parity remain open.

## R19 local developer start
Requirements: Windows, Node.js / npm, Python 3.13 with `psutil` available.
```powershell
cd PROJECTS\666_CYBER_DRIVE_CONTROL\r19-electron
npm install
npm start
```
No `npm install` or external programs were run by the repository publication. Run only on a trusted local machine after reviewing dependencies.
Set `KLRW_PYTHON` to the absolute path of the tested Python 3.13 virtual environment if the default Python command is not found.

## Boundaries
Existing R18 features must not be deleted or substituted. The R19 read-only engine currently samples **physical devices** through psutil; it does not claim a physical device counter is a Windows logical drive letter. GUI shows real live values only if bridge successfully starts. No artificial success values. Failure state displayed clearly. Host measurements remain open.

## Next executable steps
1. Import the full **R18-UNIFIED-CYBER-CONTROL** tree to `r18-legacy/` file-by-file, including tests and Windows batch launcher, with before/after hash inventory. **Pending — not in this initial git commit**.
2. Integrate R18 Windows PDH LogicalDisk adapter through versioned read-only bridge; preserve volume UUID and hotplug selections.
3. Implement settings and hotplug UI with D/E/A/B/C parity; preserve R18 storage JSON behavior.
4. Test Electron overlay/tray and compare CPU/RAM responsiveness against R18 on the Windows host; promote only after approval.
5. Publish own verified CURRENT updates only after readback; no change of sibling projects.
