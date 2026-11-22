# R2 Testbericht — 2026-11-21

| Check | Result |
|---|---|
| Python unit/integration tests | 20/20 PASS |
| `python -m compileall -q src` | PASS |
| Wheel build (`pip wheel --no-deps --no-build-isolation`) | PASS |
| CLI `--ssd-led --count 2` | PASS |
| Real Win32 keyboard hardware | READBACK_PENDING |
| Physical SSD/disk mapping under Windows | READBACK_PENDING |
| Native Tkinter GUI interaction on Windows | READBACK_PENDING |

No background service, registry write, or repository mutation occurred.
