# R19 native A/B/C scoped integration

- A capacity: actual R18 `klrw.volumes.VolumeSampler`, percentages and status, unavailable-mount errors; read-only.
- B classic: actual R18 `klrw.ssd.indicator_hex` for total disk read/write indicator; visual preview only. Explicit lock-key changing from R18 legacy B is **not** ported or activated.
- C tools: explanatory end-user panel only; installs/updates/recovery remain external to the application in `START_BUILD_WINDOWS.bat` and `BUILD/BUILD_CONTROL.ps1`. Do not add build buttons or system mutation to Electron.
- Status: actual R18 `OverviewSampler` CPU/RAM/disk/network metrics, error shown when unavailable.
- Original R18 source tree and 288-test baseline unchanged.
- Source readback and V8 parse are checked; new Python telemetry-to-UI host execution / Windows app parity and EXE/installer acceptance remain pending.
