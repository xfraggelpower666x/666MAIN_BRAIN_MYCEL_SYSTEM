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
import threading
import queue
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
    base = Path(__file__).resolve().parents[2] / "r18-legacy"
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
    source = locate_r18_source() if not getattr(sys, 'frozen', False) else None
    if source is None and not getattr(sys, 'frozen', False):
        print(json.dumps({"protocol": PROTOCOL, "status": "source_pending",
            "volumes": [], "error": "R18 source missing: import r18-legacy or set KLRW_R18_SRC",
            "timestamp": datetime.now(timezone.utc).isoformat()}), flush=True)
        return 3
    if source is not None:
        sys.path.insert(0, str(source))
    try:
        from klrw.drive_workspace import Workspace, enumerate_drives
        from klrw.windows_logical_io import WindowsLogicalDiskSampler
    except (ImportError, OSError) as exc:
        print(json.dumps({"protocol": PROTOCOL, "status": "error", "volumes": [],
            "error": "R18 module import failed: " + str(exc)}), flush=True)
        return 4
    from klrw.ssd import DiskActivitySampler
    workspace = Workspace()
    physical_sampler = DiskActivitySampler()
    commands = queue.Queue()
    def read_commands():
        for line in sys.stdin:
            try:
                commands.put(json.loads(line))
            except (ValueError, UnicodeError):
                continue
    threading.Thread(target=read_commands, daemon=True).start()
    sampler = None
    try:
        sampler = WindowsLogicalDiskSampler()
    except (OSError, AttributeError):
        pass
    try:
        while True:
            try:
                while not commands.empty():
                    item = commands.get_nowait()
                    identifier = item.get("request_id") if isinstance(item, dict) else None
                    response = {"protocol": PROTOCOL, "type": "reply", "request_id": identifier}
                    try:
                        if not isinstance(item, dict):
                            raise ValueError("Invalid request")
                        action = item.get("action")
                        if action == "set-drive-visibility":
                            key = item.get("volume_id")
                            target = item.get("target")
                            enabled = item.get("enabled")
                            if not isinstance(key, str) or len(key) > 512 or not key:
                                raise ValueError("Invalid volume ID")
                            if target not in ("tray", "overlay") or type(enabled) is not bool:
                                raise ValueError("Only tray/overlay boolean selections are supported")
                            drive = next((d for d in enumerate_drives() if d.key == key), None)
                            if drive is None:
                                raise ValueError("Drive no longer present")
                            workspace.preferences(drive)[target] = enabled
                        elif action == "set-overlay-layout":
                            layout = item.get("layout")
                            if layout not in ("minimal", "horizontal", "vertical"):
                                raise ValueError("Invalid overlay layout")
                            workspace.data["overlay"]["layout"] = layout
                        else:
                            raise ValueError("Unsupported command")
                        workspace.save()
                        response["ok"] = True
                    except (OSError, ValueError, TypeError) as exc:
                        response["ok"] = False
                        response["error"] = str(exc)
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                sample = snapshot(workspace, enumerate_drives, sampler)
                physical = []
                for device in physical_sampler.devices():
                    rate = physical_sampler.sample(device)
                    read, write = normalize_rates(rate)
                    physical.append({"id": device, "read_bps": read, "write_bps": write})
                sample["physical"] = physical
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
