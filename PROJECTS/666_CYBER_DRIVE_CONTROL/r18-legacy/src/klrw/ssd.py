"""SSD-LED-inspired optical drive activity indicator; independent original code.

Per-device counters are obtained with psutil, not copied from SSD-LED C#.
UI displays a virtual indicator only; no disk writes or keyboard changes.
"""
from dataclasses import dataclass
import math
import time
import psutil


@dataclass(frozen=True)
class DiskRates:
    device: str
    read_bps: float
    write_bps: float


@dataclass(frozen=True)
class IndicatorSettings:
    device: str = "_total"
    saturation_kib: float = 1024.0
    mix_colors: bool = True

    def validate(self):
        if not isinstance(self.device, str) or not self.device or len(self.device) > 256:
            raise ValueError("Invalid disk selection")
        if not isinstance(self.saturation_kib, (int, float)) or not math.isfinite(self.saturation_kib) or self.saturation_kib <= 0:
            raise ValueError("saturation_kib must be a positive finite number")
        if type(self.mix_colors) is not bool:
            raise ValueError("mix_colors must be boolean")


class DiskActivitySampler:
    """Monotonic counter deltas. A missing disk produces no activity, not a false disk."""
    def __init__(self, ps=psutil, clock=time.monotonic):
        self.ps, self.clock = ps, clock
        self.last = {}

    def devices(self):
        data = self.ps.disk_io_counters(perdisk=True) or {}
        return ("_total", *sorted(data))

    def sample(self, device="_total"):
        if device == "_total":
            io = self.ps.disk_io_counters()
        else:
            io = (self.ps.disk_io_counters(perdisk=True) or {}).get(device)
        now = self.clock()
        prev = self.last.get(device)
        rates = (0., 0.)
        if io is not None and prev is not None:
            last_time, last_read, last_write = prev
            dt = now - last_time
            if dt > 0 and io.read_bytes >= last_read and io.write_bytes >= last_write:
                rates = ((io.read_bytes-last_read)/dt, (io.write_bytes-last_write)/dt)
        if io is None:
            self.last.pop(device, None)
        else:
            self.last[device] = (now, io.read_bytes, io.write_bytes)
        return DiskRates(device, *rates)


def indicator_rgb(rates: DiskRates, settings: IndicatorSettings) -> tuple[int, int, int]:
    """Write=red, read=green; brightness based on configured throughput."""
    settings.validate()
    maximum = settings.saturation_kib * 1024.
    read = round(255 * min(1., max(0., rates.read_bps) / maximum))
    write = round(255 * min(1., max(0., rates.write_bps) / maximum))
    if settings.mix_colors:
        return (write, read, 0)
    return (write, 0, 0) if write >= read else (0, read, 0)


def indicator_hex(rates: DiskRates, settings: IndicatorSettings) -> str:
    return "#{:02x}{:02x}{:02x}".format(*indicator_rgb(rates, settings))
