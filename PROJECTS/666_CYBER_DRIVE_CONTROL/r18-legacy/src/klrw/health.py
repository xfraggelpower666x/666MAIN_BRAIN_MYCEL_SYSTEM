"""Read-only optional SMART health adaptation. No daemon, install, writes, or probes on import."""
from dataclasses import dataclass
from collections import deque
import json
import math
import os
import shutil
import subprocess
import time


@dataclass(frozen=True)
class HealthSnapshot:
    device: str
    temperature_c: float | None
    passed: bool | None
    available: bool
    warning: str = ""


def parse_smartctl(data: dict, device: str = "") -> HealthSnapshot:
    """Normalize smartctl --json output without claiming all devices expose all fields."""
    if not isinstance(data, dict):
        raise ValueError("Expected SMART JSON object")
    temp = data.get("temperature", {})
    temp = temp.get("current") if isinstance(temp, dict) else None
    if not isinstance(temp, (int, float)) or isinstance(temp, bool) or not math.isfinite(temp) or not -40 <= temp <= 150:
        temp = None
    status = data.get("smart_status")
    passed = status.get("passed") if isinstance(status, dict) else None
    if type(passed) is not bool: passed = None
    messages = data.get("messages", [])
    warnings = [str(m.get("string", ""))[:160] for m in messages if isinstance(m, dict) and m.get("severity") in ("error", "warning")] if isinstance(messages, list) else []
    available = passed is not None or temp is not None
    return HealthSnapshot(device=device, temperature_c=temp, passed=passed, available=available, warning="; ".join(warnings)[:240])


class SmartctlReader:
    """Explicit opt-in. Only trusted installed smartctl, no shell or auto-drive scan."""
    def __init__(self, *, enabled: bool = False, executable: str | None = None, run=subprocess.run):
        self.enabled, self.executable, self.run = enabled, executable, run

    def read(self, device: str) -> HealthSnapshot:
        if not self.enabled: raise PermissionError("SMART collection disabled; explicit opt-in required")
        if not isinstance(device, str) or not device or len(device) > 128 or device.startswith("-") or any(ord(c)<32 for c in device):
            raise ValueError("Invalid device identifier")
        exe = self.executable or shutil.which("smartctl")
        if not exe: raise FileNotFoundError("smartctl not installed")
        result = self.run([exe, "-a", "-j", device], capture_output=True, text=True, timeout=8, check=False)
        # smartctl can set warning bits in its exit code even while emitting valid SMART JSON
        if len(result.stdout) > 1024*1024: raise ValueError("SMART output too large")
        try: obj = json.loads(result.stdout)
        except (ValueError, TypeError) as ex: raise RuntimeError("SMART JSON unavailable") from ex
        return parse_smartctl(obj, device)


class HealthHistory:
    """Bounded in-memory history only. No telemetry, persistent writes or health predictions."""
    def __init__(self, capacity: int = 120):
        if not 1 <= capacity <= 10000: raise ValueError("capacity out of bounds")
        self.values = deque(maxlen=capacity)

    def add(self, snapshot: HealthSnapshot, timestamp: float | None = None):
        self.values.append((time.monotonic() if timestamp is None else timestamp, snapshot))
        return len(self.values)

    def temperatures(self, device: str):
        return tuple((t, s.temperature_c) for t, s in self.values if s.device == device and s.temperature_c is not None)
