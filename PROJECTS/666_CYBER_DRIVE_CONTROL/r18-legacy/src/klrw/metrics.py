"""Psutil-powered Windows system sampling. Rates are bytes per second."""
import time
from dataclasses import dataclass
import psutil

@dataclass(frozen=True)
class Sample:
    cpu: float
    memory: float
    disk_read: float
    disk_write: float
    network_rx: float
    network_tx: float

class SystemSampler:
    def __init__(self, ps=psutil, clock=time.monotonic):
        self.ps = ps
        self.clock = clock
        self.previous = None

    def sample(self) -> Sample:
        now = self.clock()
        disk = self.ps.disk_io_counters()
        net = self.ps.net_io_counters()
        cpu = float(self.ps.cpu_percent(interval=None))
        mem = float(self.ps.virtual_memory().percent)
        rates = (0., 0., 0., 0.)
        if self.previous:
            old_time, old_disk, old_net = self.previous
            dt = now - old_time
            if dt > 0 and disk is not None and net is not None and old_disk is not None and old_net is not None:
                values = ((disk.read_bytes, old_disk.read_bytes),
                          (disk.write_bytes, old_disk.write_bytes),
                          (net.bytes_recv, old_net.bytes_recv),
                          (net.bytes_sent, old_net.bytes_sent))
                rates = tuple(max(0, a-b)/dt for a, b in values)
        self.previous = (now, disk, net)
        return Sample(cpu, mem, *rates)
