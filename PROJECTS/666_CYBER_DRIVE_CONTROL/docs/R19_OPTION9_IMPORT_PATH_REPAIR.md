# R19 Option 9 — import path repair (2026-11-22)

## Confirmed defect
`scripts/R18_IMPORT_AND_VERIFY.py` is located at
`<checkout>/PROJECTS/666_CYBER_DRIVE_CONTROL/scripts/R18_IMPORT_AND_VERIFY.py`.
The original `parents[3]` points to the directory **above** the Git root, so
`(repo/'.git').exists()` incorrectly fails with `Not a Git checkout`.

## Minimal fix
Use `parents[2]`, which addresses `<checkout>` for this repository layout.
The subtree import destination, source ZIP hash hardlock, count check, temporary
pytest run, byte-by-byte hash verification, and scoped publisher remain unchanged.

## Verification scope
- Directory-level source path reasoning checked against the actual repository path.
- Current GitHub source was retrieved and its exact changed lines inspected.
- This fix is a repository-source repair, **not** evidence of a Windows build.
- Windows option 9 remains pending end-to-end host execution and proof of a real
  `r18-legacy` GitHub readback; no EXE or installer is claimed.

## Known gates
- Original R18 ZIP has 186 entries and SHA-256
  `0364d38d1fe41492bad821e636d0c089be13ac0304a9fcf01761c79d4d2fce8b`.
- Python environment with pytest and working Windows Git checkout required.
- A concurrent push aborts the scoped publisher; do not force-push.
