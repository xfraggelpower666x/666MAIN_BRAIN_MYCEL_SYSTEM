"""Gemeinsames read-only Statusmodell für Windows Tray und Desktop (R13)."""
from dataclasses import dataclass
import math
from .lock_indicator import LockSnapshot
from .rgb_layers import RGBPolicy
from .ssd import DiskRates
from .network_directions import NetworkRates
from .status_snapshot import lock_tiles, disk_tiles, network_tiles


def _rate(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Rates must be finite")
    return max(0.0, value)


@dataclass(frozen=True)
class UnifiedFrame:
    locks: LockSnapshot
    disk: DiskRates
    network: NetworkRates
    cpu_pct: float
    memory_pct: float
    rgb: tuple[int, int, int]
    rgb_source: str
    layer: int
    tiles: tuple
    tooltip: str
    fingerprint: tuple


def compose_frame(locks, disk, network, cpu_pct=0, memory_pct=0, *, layer=0,
                  order="NCS", disk_threshold_bps=1, network_threshold_bps=1,
                  rgb_policy=None, disk_settings=None):
    """Berechnet reine Anzeigedaten; keine physischen LED- oder HID-Schreibzugriffe."""
    if not isinstance(locks, LockSnapshot) or not isinstance(disk, DiskRates) or not isinstance(network, NetworkRates):
        raise TypeError("Invalid monitor snapshot")
    if type(layer) is not int or layer not in range(4):
        raise ValueError("layer must be 0..3")
    if not math.isfinite(float(cpu_pct)) or not math.isfinite(float(memory_pct)):
        raise ValueError("Invalid percentage")
    if disk_threshold_bps < 0 or network_threshold_bps < 0:
        raise ValueError("Negative activity threshold")
    disk = DiskRates(disk.device, _rate(disk.read_bps), _rate(disk.write_bps))
    network = NetworkRates(network.interface, _rate(network.rx_bps), _rate(network.tx_bps))
    rgb_frame = (rgb_policy or RGBPolicy()).render((layer,), bool(locks.caps))
    tiles = (*lock_tiles(locks,order), *disk_tiles(disk,disk_threshold_bps),
             *network_tiles(network,network_threshold_bps))
    percent = lambda v: min(100.,max(0.,float(v)))
    cpu, mem = percent(cpu_pct), percent(memory_pct)
    label = (f"Locks N:{int(locks.num)} C:{int(locks.caps)} S:{int(locks.scroll)} | "
             f"Disk R:{disk.read_bps/1024:.1f} W:{disk.write_bps/1024:.1f} KiB/s | "
             f"Net RX:{network.rx_bps/1024:.1f} TX:{network.tx_bps/1024:.1f} KiB/s | "
             f"RGB:{rgb_frame.source} L{layer} | CPU:{cpu:.0f}% RAM:{mem:.0f}%")
    # Exclude rates from fingerprint until rounded as these fluctuate every sample.
    fingerprint = (tuple((t.name,t.active) for t in tiles), layer, rgb_frame.color,
                   round(cpu),round(mem),round(disk.read_bps/1024),round(disk.write_bps/1024),
                   round(network.rx_bps/1024),round(network.tx_bps/1024),disk.device,network.interface)
    return UnifiedFrame(locks,disk,network,cpu,mem,rgb_frame.color,rgb_frame.source,layer,
                        tuple(tiles),label,fingerprint)


def icon_colors(frame):
    """Neun Quadrate: N/C/S, Disk R/W, Net RX/TX, RGB, health-neutral."""
    if not isinstance(frame, UnifiedFrame):
        raise TypeError("frame must be UnifiedFrame")
    locks = frame.locks
    return ((35,224,160) if locks.num else (69,77,91),
            (35,224,160) if locks.caps else (69,77,91),
            (35,224,160) if locks.scroll else (69,77,91),
            (33,202,113) if frame.disk.read_bps > 0 else (69,77,91),
            (239,69,96) if frame.disk.write_bps > 0 else (69,77,91),
            (33,200,255) if frame.network.rx_bps > 0 else (69,77,91),
            (255,122,204) if frame.network.tx_bps > 0 else (69,77,91),
            frame.rgb, (30,40,56))
