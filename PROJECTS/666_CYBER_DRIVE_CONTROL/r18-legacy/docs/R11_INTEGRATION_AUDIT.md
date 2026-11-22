# R11 Source audit (2026-11-21)

- `odomobo/HddTaskMonitor`: Windows tray icon showing free GB (MIT). Adopt capacity status logic, not code. Source `README.md`.
- `sendust/hdd_monitor`: Windows Python per-volume I/O including mapped network drives; also CPU/available memory, 0.5s display and tray. License not declared in GitHub metadata. R10 already handles per-disk I/O; avoid copying Windows PDH/WMI code. Source `README.md` and `disk_mini.py`.
- `blackbone23/hdd_monitor_script`: capacity threshold alarms and cron. Original script sends disk metadata to remote HTTP URL and probes external service; no network transfer, cron, SSH, or legacy code imported. Source `psutil_disk_usage_alarm.py`. No license verified.
- `iuristanchev/py_mon`: CPU/RAM/disk usage and graphing, but source includes unconditional periodic HTTP request to external host. No requests/logging side effects imported. Source `monitoring.py`. No license verified.

## Implemented

New independent, optional local read-only capacity sampler (`volumes.py`), JSON/text CLI (`capacity_cli.py`), and Tk desktop window (`capacity_window.py`), with test injection, per-volume errors, thresholds, opt-in remote mounts, and no background services or HTTP requests.

## Verification boundaries

Linux tests verify source behavior and fake psutil. Native Windows paths, Tk UI, network shares, ACL handling and installer behavior remain READBACK_PENDING. No external GitHub repo mutation. No foreign source-code copy. Existing R10 code retained.
