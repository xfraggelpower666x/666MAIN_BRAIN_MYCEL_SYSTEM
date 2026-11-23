# R19 v2 — application integration

Electron main launches `bridge/volume_metrics.py` and accepts only `cyber-drive.metrics.v2` records. The view renders letter, label, GUID-derived identity and R/W measurements without substituting physical disk names for drive letters. Missing counters stay `null`, and the UI shows 'Unavailable'.

The bridge loads actual R18 `klrw` modules from `r18-legacy/src` or from `KLRW_R18_SRC` (full path to an existing validated R18 `src`). Source import into GitHub remains pending, so R19 will show a SOURCE_PENDING state until a verified R18 source tree is present. This is deliberate fail-closed behavior, not a hidden demo.

Non-destructive: existing R18 GUI remains available; no keyboard hardware write; no setup/pip/npm action executed by GitHub publishing.

Local tests: existing R18 `test_drive_workspace.py` + `test_windows_logical_io.py` passed 9/9 on Linux mocked/adapted tests. R19 bridge contract test and Windows host GUI readback are pending execution; no claim of full regression or native Windows test.
