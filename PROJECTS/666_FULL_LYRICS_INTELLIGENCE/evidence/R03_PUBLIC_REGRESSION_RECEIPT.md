# R03 public fixture-safe regression

Local original R03 copy with private R02 DB: 10/10 PASS.
Local isolated copy containing only engine/bridge.py and tests (no legacy DB): 9/9 PASS, private legacy test explicitly NOT RUN.

Command: `python tests/run_portable_regression.py`

Source: `tests/run_portable_regression.py` plus original `tests/test_engine.py`.
Scope: local execution only; GitHub CI not configured; no Windows Electron host acceptance.
