#!/usr/bin/env python3
"""R19 v2: read-only bridge to the actual R18 Windows drive modules.

Emits newline-delimited JSON. Uses R18's GUID-backed inventory, persisted drive
visibility, and PDH LogicalDisk counters when R18 source is available.
No keys, hardware LEDs or disk contents are changed.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

PROTOCOL = "cyber-drive.metrics.v2"


def locate_r18_source():
    explicit = os.environ.get("KLRW_R18_SRC", "")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if (path / "klrw" / "drive_workspace.py").is_file():
            return path
        if (path / "src" / "klrw" / "drive_workspace.py").is_file():
            return path / "src"
    base = Path(__file__).resolve().parents[3] / "r18-legacy"
    if (base / "src" / "klrw" / "drive_workspace.py").is_file():
        return base / "src"
    return None


def normalize_rates(value):
    """Only validated, finite non-negative rates are exposed."""
    import math
    def clean(n):
        try:
            n = float(n)
            return round(n, 1) if math.isfinite(n) and n >= 0 else None
        except (TypeError, ValueError, OverflowError):
            return None
    if value is None:
        return None, None
    return clean(value.read_bps), clean(value.write_bps)


def snapshot(workspace, inventory, sampler, *, timestamp=None):
    volumes = []
    drives = inventory()
    letters = {d.mount.upper() for d in drives if len(d.mount) == 2 and d.mount[1] == ":"}
    rates = {}
    source_error = None
    if sampler is not None:
        try:
            sampler.configure(letters)
            rates = sampler.sample_all()
        except (OSError, ValueError, RuntimeError) as exc:
            source_error = type(exc).__name__ + ": " + str(exc)
    for d in drives:
        prefs = workspace.preferences(d)
        rate = rates.get(d.mount.upper())
        read, write = normalize_rates(rate)
        volumes.append({
            "id": d.key, "letter": d.mount, "label": d.label,
            "filesystem": d.filesystem, "removable": d.removable,
            "targets": {k: bool(prefs.get(k, False)) for k in ("tray", "overlay", "keyboard")},
            "measurement": "logical_pdh" if read is not None and write is not None else "unavailable",
            "read_bps": read, "write_bps": write
        })
    return {
        "protocol": PROTOCOL, "status": "ok", "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "source": "R18 Workspace + Windows LogicalDisk PDH" if sampler is not None else "R18 Workspace; PDH unavailable",
        "error": source_error, "volumes": volumes,
        "settings": {
            "activity_threshold_bps": workspace.data["activity_threshold_bps"],
            "led_hold_ms": workspace.data["led_hold_ms"],
            "led_quiet_ms": workspace.data["led_quiet_ms"],
            "overlay": dict(workspace.data["overlay"])
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Single snapshot for diagnostics")
    args = parser.parse_args()
    source = locate_r18_source()
    if source is None:
        print(json.dumps({"protocol": PROTOCOL, "status": "source_pending",
            "volumes": [], "error": "R18 source missing: import r18-legacy or set KLRW_R18_SRC",
            "timestamp": datetime.now(timezone.utc).isoformat()}), flush=True)
        return 3
    sys.path.insert(0, str(source))
    try:
        from klrw.drive_workspace import Workspace, enumerate_drives
        from klrw.windows_logical_io import WindowsLogicalDiskSampler
    except (ImportError, OSError) as exc:
        print(json.dumps({"protocol": PROTOCOL, "status": "error", "volumes": [],
            "error": "R18 module import failed: " + str(exc)}), flush=True)
        return 4
    workspace = Workspace()
    sampler = None
    try:
        sampler = WindowsLogicalDiskSampler()
    except (OSError, AttributeError):
        pass
    try:
        while True:
            try:
                sample = snapshot(workspace, enumerate_drives, sampler)
                print(json.dumps(sample, ensure_ascii=False, separators=(",", ":")), flush=True)
            except (OSError, ValueError, RuntimeError) as exc:
                print(json.dumps({"protocol": PROTOCOL, "status": "error", "volumes": [],
                    "error": str(exc)}), flush=True)
            if args.once:
                break
            time.sleep(0.5)
    finally:
        if sampler is not None:
            sampler.close()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
