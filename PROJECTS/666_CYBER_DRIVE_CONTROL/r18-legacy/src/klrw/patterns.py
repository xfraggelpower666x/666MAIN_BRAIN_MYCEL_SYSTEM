"""Hardware-independent, deterministic three-indicator animation schedules.

Patterns are authored independently from hexwell/kb (unlicensed) and
Christux/KeyboardLedMonitor (GPL-2.0-or-later). Never inject keys here.
"""
from dataclasses import dataclass

LEDS = ('num', 'caps', 'scroll')


@dataclass(frozen=True)
class Frame:
    num: bool
    caps: bool
    scroll: bool
    duration_ms: int = 150

    def __post_init__(self):
        if any(type(v) is not bool for v in (self.num, self.caps, self.scroll)):
            raise ValueError('all LED values must be boolean')
        if type(self.duration_ms) is not int or not 20 <= self.duration_ms <= 10000:
            raise ValueError('duration_ms must be 20..10000')

    def states(self):
        return dict(zip(LEDS, (self.num, self.caps, self.scroll)))


def sequence(mode: str, duration_ms=150):
    """Produce one finite cycle without accessing hardware or sleeping."""
    if type(duration_ms) is not int or not 20 <= duration_ms <= 10000:
        raise ValueError('duration_ms must be 20..10000')
    patterns = {
        'chase': ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        'bounce': ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 0)),
        'fill': ((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 1, 0), (1, 0, 0)),
        'center': ((0, 1, 0), (1, 1, 1), (0, 1, 0), (0, 0, 0)),
        'pulse': ((0, 0, 0), (1, 1, 1), (0, 0, 0)),
    }
    if mode not in patterns:
        raise ValueError('unknown pattern')
    return tuple(Frame(*(bool(v) for v in values), duration_ms=duration_ms) for values in patterns[mode])


def meter(value: float, maximum: float = 100.0, duration_ms: int = 150):
    """Three-position capacity bar; any valid metric can be normalized."""
    import math
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v)
           for v in (value, maximum)) or maximum <= 0:
        raise ValueError('value and maximum must be finite numbers; maximum > 0')
    if value < 0:
        raise ValueError('value must be >= 0')
    ratio = min(value / maximum, 1.0)
    n = 0 if ratio == 0 else min(3, math.ceil(ratio * 3))
    return Frame(*(i < n for i in range(3)), duration_ms=duration_ms)
