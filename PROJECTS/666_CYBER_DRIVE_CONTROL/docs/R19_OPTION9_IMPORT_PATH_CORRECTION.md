# Option 9: verified path correction (supersedes previous repair)

The prior statement that `parents[3]` was too high is **incorrect**. The actual Python `pathlib.Path.parents` indexing from
`/checkout/PROJECTS/666_CYBER_DRIVE_CONTROL/scripts/R18_IMPORT_AND_VERIFY.py` is:

- `parents[0]` = `.../scripts`
- `parents[1]` = `.../666_CYBER_DRIVE_CONTROL`
- `parents[2]` = `.../PROJECTS`
- `parents[3]` = `/checkout` — **correct Git repository root**

The previous change to `parents[2]` would incorrectly reject a valid Git checkout. The importer is now restored to `parents[3]`, with the destination retained as `parents[1]/r18-legacy`. A new Python regression test checks both paths.

This is a **source correction**, not proof that option 9 executed on Windows or that R18 source was pushed into GitHub. Original source ZIP SHA/186-file guard and subsequent 288-test gate are unchanged. Release remains BUILD_BLOCKED until R18 is imported to the Git working tree and published, then a Windows build passes.
