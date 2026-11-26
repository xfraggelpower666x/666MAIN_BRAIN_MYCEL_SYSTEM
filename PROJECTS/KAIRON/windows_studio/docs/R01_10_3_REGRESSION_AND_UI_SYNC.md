# R01.10.3 — Regression suite and UI release synchronization

## Source basis
Continued from the complete R01.10.2 package. Existing project identity, folder layout,
PowerShell build engine, Electron packaging flow and user-supplied cleaned boot artwork
are retained.

## Repairs
- Replaced three obsolete boot tests that still asserted the retired Panel/legacy-control
  implementation with assertions for the current single-PictureBox Paint architecture.
- Added explicit checks for one-time artwork loading, the existing asset path, 8-second
  timing, phase ordering, progress-state updates, stale-reference absence, Electron config
  parity and visible GUI release labels.
- Updated stale R01.7 labels in the menu to R01.10.3.
- Updated the cyber-boot window label and initialized progress state to 0%.

## Verification
- Python unittest suite: run during package preparation.
- ZIP integrity and SHA-256 manifest: verified after packaging.
- Windows PowerShell/WinForms execution, Electron runtime, Portable EXE and NSIS setup:
  still require a real Windows host; not claimed as passed.
