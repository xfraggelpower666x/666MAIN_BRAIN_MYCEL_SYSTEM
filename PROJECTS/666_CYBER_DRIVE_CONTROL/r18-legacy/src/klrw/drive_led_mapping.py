"""Drive activity -> optional lock LED mapping. Pure logic, no hardware effects."""
from dataclasses import dataclass
from .ssd import DiskRates

LEDS = ('caps', 'num', 'scroll')
MODES = ('off', 'read', 'write', 'either')

@dataclass(frozen=True)
class DriveBinding:
    led: str
    drive: str
    mode: str = 'off'
    threshold_kib: float = 4.0

    def validate(self):
        import math
        if self.led not in LEDS or self.mode not in MODES:
            raise ValueError('Invalid LED or drive activity mode')
        if not isinstance(self.drive, str) or not self.drive or len(self.drive) > 256:
            raise ValueError('Invalid drive name')
        if not isinstance(self.threshold_kib, (float, int)) or not math.isfinite(self.threshold_kib) or self.threshold_kib < 0:
            raise ValueError('Invalid activity threshold')


def evaluate(bindings, rates_by_drive):
    """Return lock targets from per-drive read/write byte rates; off always false."""
    result = {}
    for binding in bindings:
        binding.validate()
        if binding.led in result:
            raise ValueError('Duplicate LED mapping')
        rates = rates_by_drive.get(binding.drive, DiskRates(binding.drive, 0.0, 0.0))
        threshold = binding.threshold_kib * 1024.0
        read = rates.read_bps > threshold
        write = rates.write_bps > threshold
        result[binding.led] = (read if binding.mode == 'read' else
                               write if binding.mode == 'write' else
                               (read or write) if binding.mode == 'either' else False)
    return result
