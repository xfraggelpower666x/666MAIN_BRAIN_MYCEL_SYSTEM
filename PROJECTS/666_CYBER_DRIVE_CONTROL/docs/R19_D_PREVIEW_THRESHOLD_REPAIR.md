# R19 D — source-level preview threshold repair

Found in `r19-electron/renderer.js`: the D preview compared every saved Caps/Num/Scroll mode against `last.settings.activity_threshold_bps`, ignoring the persisted `threshold_kib` per binding. Missing physical devices also caused an in-memory mutation of `last.bindings` during render.

Repair: `bindingActive` uses the original R18 DriveBinding threshold semantics (KiB/s * 1024), finite validated rates and per-mode read/write evaluation; missing drives render OFF. The selected fallback device is display-only and never overwrites the saved binding. No keyboard hardware endpoints were introduced.

Verification gate: `tests/test_r19_renderer_contract.cjs` uses Node's builtin test runner against the function extracted from the actual renderer source. The central Windows build now runs the test before packaging. No production Windows EXE runtime or installation is claimed.
