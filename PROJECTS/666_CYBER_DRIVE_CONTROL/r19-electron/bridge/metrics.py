#!/usr/bin/env python3
"""R19 read-only metrics bridge. Emits one JSON record per line; no hardware writes."""
import json
import sys
import time
from datetime import datetime, timezone

def output(record):
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)

def main():
    try:
        import psutil
    except ImportError:
        output({"status": "error", "disks": [], "error": "psutil is missing from selected Python", "timestamp": None})
        return 2
    prior = {}
    prior_at = time.monotonic()
    while True:
        try:
            now = time.monotonic()
            current = psutil.disk_io_counters(perdisk=True) or {}
            seconds = max(now - prior_at, 0.001)
            disks = []
            for name, sample in sorted(current.items()):
                old = prior.get(name)
                rbps = max(0, (sample.read_bytes - old.read_bytes) / seconds) if old else 0
                wbps = max(0, (sample.write_bytes - old.write_bytes) / seconds) if old else 0
                disks.append({"name": str(name), "read_bps": round(rbps, 1), "write_bps": round(wbps, 1)})
            prior = current
            prior_at = now
            output({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "psutil.disk_io_counters(perdisk=True)", "disks": disks})
            time.sleep(0.5)
        except (OSError, ValueError) as exc:
            output({"status": "error", "disks": [], "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat()})
            time.sleep(2)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
