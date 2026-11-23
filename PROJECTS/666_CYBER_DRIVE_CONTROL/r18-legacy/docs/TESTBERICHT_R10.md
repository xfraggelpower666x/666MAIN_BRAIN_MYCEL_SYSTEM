# R10 Testbericht — 2026-11-21

- `PYTHONPATH=src python -m pytest -q`: **137 passed in 2.08s**.
- `python -m compileall -q src/klrw`: PASS.
- `python -m pip wheel --no-deps --no-build-isolation`: PASS (wheel `keyboard_led_remapper_windows-1.9.0-py3-none-any.whl`).
- `PYTHONPATH=src python -m klrw.dashboard_cli`: PASS (JSON emitted with overview fields, no SMART invocation).
- Vorhandene R9-Python-Quelldateien (`src/klrw/*.py`) SHA-256-identisch: **28/28**.
- ZIP-Integritätsprüfung: wird nach Erstellung vorgenommen.
- Native Windows-GUI, echtes smartctl, S.M.A.R.T.-Controller, GPU und Treiber: **READBACK_PENDING**.
- Externe Binaries: **nicht ausgeführt**.
