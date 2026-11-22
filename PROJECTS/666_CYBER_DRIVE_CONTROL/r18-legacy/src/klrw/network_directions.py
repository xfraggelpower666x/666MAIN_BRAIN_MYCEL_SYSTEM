"""Read-only RX/TX monitoring inspired by ledcapture; no packet capture."""
from dataclasses import dataclass
import time
import psutil

@dataclass(frozen=True)
class NetworkRates:
    interface: str
    rx_bps: float
    tx_bps: float

class NetworkDirectionSampler:
    def __init__(self, ps=psutil, clock=time.monotonic):
        self.ps, self.clock, self.previous = ps, clock, {}

    def interfaces(self):
        return tuple(sorted((self.ps.net_io_counters(pernic=True) or {}).keys()))

    def sample(self, interface='_total'):
        counters = (self.ps.net_io_counters() if interface == '_total'
                    else (self.ps.net_io_counters(pernic=True) or {}).get(interface))
        now = self.clock()
        old = self.previous.get(interface)
        values = (0.0, 0.0)
        if counters is not None and old is not None:
            old_t, old_rx, old_tx = old
            dt = now - old_t
            if dt > 0 and counters.bytes_recv >= old_rx and counters.bytes_sent >= old_tx:
                values = ((counters.bytes_recv-old_rx)/dt, (counters.bytes_sent-old_tx)/dt)
        if counters is None:
            self.previous.pop(interface, None)
        else:
            self.previous[interface] = (now, counters.bytes_recv, counters.bytes_sent)
        return NetworkRates(interface, *values)

def states(rates, incoming='caps', outgoing='scroll', threshold_bps=1.0):
    if incoming not in ('caps','num','scroll') or outgoing not in ('caps','num','scroll'):
        raise ValueError('Invalid LED')
    if incoming == outgoing:
        raise ValueError('RX and TX require distinct LEDs')
    if not 0 <= threshold_bps < float('inf'):
        raise ValueError('Invalid threshold')
    return {incoming: rates.rx_bps >= threshold_bps and rates.rx_bps > 0,
            outgoing: rates.tx_bps >= threshold_bps and rates.tx_bps > 0}
