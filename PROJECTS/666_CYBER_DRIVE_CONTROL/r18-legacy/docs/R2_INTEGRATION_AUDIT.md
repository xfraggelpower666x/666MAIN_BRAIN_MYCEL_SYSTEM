# R2 · SSD-LED integration audit

## Source readback

- Linux reference: `suvanbanerjee/Keyboard-LED-Remapper`, `main`, README — LED mapping from system activity; Linux `/sys/class/leds` and systemd incompatible with Windows.
- Windows reference: `SIRprise/SSD-LED`, `master`: `README.md`, `SSD-LED/Form1.cs`, `SSD-LED/DiskActivity.cs`, `SSD-LED/IndicatorIcon.cs`, `SSD-LED/Benchmark.cs` inspected over GitHub read-only connector.
- `Form1.cs` uses Windows `PerformanceCounter` PhysicalDisk read/write byte rates and a gradient-color tray icon; `DiskActivity.cs` is a placeholder; `IndicatorIcon.cs` includes unfinished icon functionality; `Benchmark.cs` contains draft/commented benchmarking examples.
- No declared GitHub repository license observed for `SIRprise/SSD-LED`; therefore **no upstream C# source was copied**. Design ideas only, reimplemented independently with psutil.

## Non-destructive changes

- Preserved: `model.py`, `config.py`, `engine.py`, `leds.py`, `metrics.py` and their R1 tests unchanged.
- Additive: `ssd.py`, `tests/test_ssd.py`; extended `runtime.py`, `cli.py`, and `gui.py` without changing existing callback signature.
- GUI visual LED is not a tray icon. Real keyboard status LED still needs user opt-in and is not controlled by the SSD color.
- R1 JSON schema remains 1 (fully backwards compatible).

## Acceptance limitations

- Tests run in the container, not on a native Windows GUI / physical keyboard; no hardware compatibility or physical LED changes are verified.
- Device selection uses exact IDs returned by psutil. C: is NOT guaranteed to correspond to physical disk ID.
- Per-drive I/O bytes can differ by platform and privileges. Errors are isolated so the main monitor keeps operating.
- SSD-LED Windows tray icon is a potential subsequent module, not claimed to be integrated.
