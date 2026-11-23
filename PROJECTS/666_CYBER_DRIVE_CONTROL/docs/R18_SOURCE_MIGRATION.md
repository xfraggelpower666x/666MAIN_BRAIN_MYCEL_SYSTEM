# Import all R18 source files into the live project

This utility is available because the original R18 project had been delivered to the conversation as a ZIP, while the first native GitHub commit only contained the R19 frontend and its bridge. It is **not a substitute for a completed source migration**.

On a trusted Windows developer checkout:

```powershell
cd PROJECTS\666_CYBER_DRIVE_CONTROL
py -3.13 scripts\import_r18.py "B:\\Desktop\\KeyboardLEDRemapper-Windows-R18-UNIFIED-CYBER-CONTROL.zip" --dry-run
py -3.13 scripts\import_r18.py "B:\\Desktop\\KeyboardLEDRemapper-Windows-R18-UNIFIED-CYBER-CONTROL.zip"
git status --short
git diff --no-index -- /dev/null docs/R18_IMPORT_SHA256.json
```

Import is local and non-destructive. No auto git add/commit/push. All external writes require explicit Git commit; no silent publication, overwrites or ZIP archive added to Git. The command does not execute any code from the archive. After import, run existing R18 regression, check starter and test results, then publish the source files under `r18-legacy/` via normal reviewed GitHub workflow.
