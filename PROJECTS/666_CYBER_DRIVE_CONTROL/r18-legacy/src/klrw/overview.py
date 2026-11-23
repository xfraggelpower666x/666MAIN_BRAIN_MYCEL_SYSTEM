"""Consolidated read-only metrics and HTML-free presentation model."""
from dataclasses import dataclass
from .metrics import Sample, SystemSampler
from .ssd import DiskActivitySampler, DiskRates


@dataclass(frozen=True)
class Overview:
    cpu_pct: float
    memory_pct: float
    read_bps: float
    write_bps: float
    rx_bps: float
    tx_bps: float
    disk: str
    disk_read_bps: float
    disk_write_bps: float


def clamp_percentage(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def compose(sample: Sample, drive: DiskRates) -> Overview:
    return Overview(clamp_percentage(sample.cpu), clamp_percentage(sample.memory),
                    max(0., sample.disk_read), max(0., sample.disk_write),
                    max(0., sample.network_rx), max(0., sample.network_tx),
                    drive.device, max(0., drive.read_bps), max(0., drive.write_bps))


class OverviewSampler:
    def __init__(self, system=None, disks=None, device="_total"):
        self.system = system or SystemSampler()
        self.disks = disks or DiskActivitySampler()
        self.device = device

    def sample(self):
        return compose(self.system.sample(), self.disks.sample(self.device))


def colored_meter(pct: float, width: int = 10) -> str:
    if not 1 <= width <= 100: raise ValueError("width out of bounds")
    filled = round(clamp_percentage(pct)*width/100)
    return "█" * filled + "░" * (width-filled)
