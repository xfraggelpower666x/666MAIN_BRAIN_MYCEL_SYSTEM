# R12 Testbericht

- Version: 1.11.0
- **170 / 170 pytest PASS** (Linux test host, R1-R11 regression retained)
- `python -m compileall -q src`: PASS
- `python -m pip wheel . --no-deps --no-build-isolation`: PASS
- Lock-state preview CLI (CNS): PASS
- Existing R11 Python modules byteidentical: 35 / 35 PASS
- Native Windows tray/monitor handling: **READBACK_PENDING**
- Keyboard physical LED states: **READBACK_PENDING**
- No physical device was accessed, no registry writes or driver installation.
