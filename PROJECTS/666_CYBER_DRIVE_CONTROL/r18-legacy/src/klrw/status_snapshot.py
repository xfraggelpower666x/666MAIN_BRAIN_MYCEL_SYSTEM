"""Display-neutral status renderer for a future Windows tray, no OS writes."""
from dataclasses import dataclass
from .lock_indicator import parse_order

@dataclass(frozen=True)
class StatusTile:
    name: str
    active: bool
    color: str
    tooltip: str

def lock_tiles(snapshot, order='NCS'):
    values = snapshot.as_dict()
    return tuple(StatusTile(name, bool(values[name]), '#22d3a1' if values[name] else '#555555',
                            name.upper() + (' on' if values[name] else ' off')) for name in parse_order(order))

def network_tiles(rates, threshold_bps=1):
    if threshold_bps < 0: raise ValueError('Invalid threshold')
    return (StatusTile('rx',rates.rx_bps >= threshold_bps and rates.rx_bps > 0,'#21c8ff','Incoming bytes/sec'),
            StatusTile('tx',rates.tx_bps >= threshold_bps and rates.tx_bps > 0,'#ff7acc','Outgoing bytes/sec'))

def disk_tiles(rates, threshold_bps=1):
    if threshold_bps < 0: raise ValueError('Invalid threshold')
    return (StatusTile('read',rates.read_bps >= threshold_bps and rates.read_bps > 0,'#21ca71','Disk read bytes/sec'),
            StatusTile('write',rates.write_bps >= threshold_bps and rates.write_bps > 0,'#ef4560','Disk write bytes/sec'))
