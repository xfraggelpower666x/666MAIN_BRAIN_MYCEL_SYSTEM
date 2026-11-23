"""Deterministic read-only disk activity presentation (R9)."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ActivityVisual:
    read_bps: float
    write_bps: float
    read_level: int
    write_level: int
    hex_color: str
    status: str


def _rate(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("rate must be a finite nonnegative number")
    return float(value)


def activity_visual(read_bps, write_bps, saturation_kib=1024):
    """Read=green, write=red, saturation scales independently. Never performs I/O."""
    r, w = _rate(read_bps), _rate(write_bps)
    s = _rate(saturation_kib)
    if not s: raise ValueError("saturation must be positive")
    max_bps = s * 1024.0
    read_level = min(255, int(round(255 * min(1, r / max_bps))))
    write_level = min(255, int(round(255 * min(1, w / max_bps))))
    status = "read+write" if r and w else ("read" if r else ("write" if w else "idle"))
    return ActivityVisual(r, w, read_level, write_level, f"#{write_level:02x}{read_level:02x}00", status)


def summarize_devices(rates):
    """Pure per-device aggregation without silently counting _total twice."""
    total_read = total_write = 0.0
    for device, pair in rates.items():
        if device == "_total": continue
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("expected (read_bps, write_bps) for each disk")
        total_read += _rate(pair[0]); total_write += _rate(pair[1])
    return (total_read, total_write)


def activity_frame(read_bps, write_bps, phase=0, saturation_kib=1024):
    """Two-step appearance modulation only; real metrics are never synthesized."""
    visual = activity_visual(read_bps, write_bps, saturation_kib)
    if phase not in (0, 1): raise ValueError("phase must be 0 or 1")
    factor = 1.0 if phase == 0 else 0.60
    return f"#{round(visual.write_level*factor):02x}{round(visual.read_level*factor):02x}00"
