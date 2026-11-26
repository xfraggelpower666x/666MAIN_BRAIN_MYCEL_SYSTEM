"""Local read-only desktop telemetry for the existing 3DX / Resin3 GUI.

No socket, private settings, provider passwords, URLs, or process spawning.
"""
import json
import math
import os
import time
from ..config import DATA_DIR

SCHEMA = "666.streamtranscoder.desktop-status.v1"
STATUS_FILE = DATA_DIR / "desktop-status-v1.json"
COMPONENTS = ("source", "monitor", "encoder", "server", "relay", "error")
STATES = {"off", "live", "connecting", "error"}
EVENT_STATES = {"active", "connected", "connecting", "starting", "retrying", "error", "idle", "off"}

def dbfs(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return round(max(-120., min(12., float(value))), 1)

def sanitized_snapshot(*, status="off", broadcaster=None, monitor=None,
                       input_dbfs=None, output_dbfs=None, timestamp=None):
    live = bool(broadcaster is not None and getattr(broadcaster, "live", False))
    state = status if status in STATES else "off"
    if state == "live" and not live:
        state = "off"
    bus = getattr(broadcaster, "status_bus", None)
    events = bus.snapshot() if bus is not None else {}
    components = {}
    for key in COMPONENTS:
        event_state = getattr(events.get(key), "state", "unknown")
        components[key] = event_state if event_state in EVENT_STATES else "unknown"
    return {"schema": SCHEMA, "timestamp_ms": int((time.time() if timestamp is None else timestamp)*1000),
            "pid": os.getpid(), "status": state, "on_air": bool(live and state == "live"),
            "monitor_active": bool(monitor is not None and getattr(monitor, "running", False)),
            "input_dbfs": dbfs(input_dbfs), "output_dbfs": dbfs(output_dbfs),
            "components": components}

def write_desktop_status(**kwargs):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_FILE.with_name(STATUS_FILE.name + "." + str(os.getpid()) + ".tmp")
    try:
        tmp.write_text(json.dumps(sanitized_snapshot(**kwargs), separators=(",", ":")), encoding="utf-8")
        os.replace(tmp, STATUS_FILE)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass

def remove_desktop_status():
    try:
        data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        if data.get("pid") == os.getpid():
            STATUS_FILE.unlink(missing_ok=True)
    except (OSError, ValueError, AttributeError):
        pass
