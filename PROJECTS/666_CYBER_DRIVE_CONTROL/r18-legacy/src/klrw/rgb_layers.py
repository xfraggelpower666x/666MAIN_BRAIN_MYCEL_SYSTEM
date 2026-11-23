"""Optional RGB priority policy inspired by Silakka54 QMK, without firmware access.

The module NEVER opens HID, serial or USB devices. Only preview color computation.
No QMK files or firmware code are copied. Host lock state is separate from
physical keyboard LED states. A future RGB adapter needs a documented protocol.
"""
from dataclasses import dataclass

RGB = tuple[int, int, int]
OFF: RGB = (0, 0, 0)
BLUE: RGB = (0, 90, 255)
GREEN: RGB = (0, 230, 90)
PURPLE: RGB = (150, 0, 230)
RED: RGB = (255, 0, 0)


@dataclass(frozen=True)
class RGBFrame:
    color: RGB
    source: str
    layer: int

    @property
    def hex(self) -> str:
        return '#%02X%02X%02X' % self.color


class RGBPolicy:
    """Caps wins over keyboard layer, no stale priorities after state changes.

    Default layer 0 off; highest active of layers 1-3 determines base color.
    Caps lock is an overlay and never changes the functional key state.
    """
    def __init__(self, colors=None):
        self.colors = dict({0: OFF, 1: BLUE, 2: GREEN, 3: PURPLE} if colors is None else colors)
        if set(self.colors) != {0, 1, 2, 3}:
            raise ValueError('palette must contain layer keys 0, 1, 2, 3')
        for color in self.colors.values():
            validate_color(color)

    def render(self, active_layers=(), caps_lock=False):
        layers = tuple(active_layers)
        if any(type(n) is not int or n not in range(4) for n in layers):
            raise ValueError('active layers must be integers 0..3')
        if type(caps_lock) is not bool:
            raise ValueError('caps_lock must be boolean')
        layer = max(layers, default=0)
        if caps_lock:
            return RGBFrame(RED, 'caps_lock', layer)
        return RGBFrame(self.colors[layer], 'layer', layer)


def validate_color(color):
    if not isinstance(color, (tuple, list)) or len(color) != 3 or any(type(x) is not int or x < 0 or x > 255 for x in color):
        raise ValueError('RGB must be three integer channels in [0,255]')


class RGBPreview:
    """Stateful simulator; independent units emulate split halves without USB writes."""
    def __init__(self, units=2, synchronized=False, policy=None):
        if type(units) is not int or units < 1 or units > 32:
            raise ValueError('units must be 1..32')
        self.units = units
        self.synchronized = bool(synchronized)
        self.policy = policy or RGBPolicy()
        self._frames = [self.policy.render() for _ in range(units)]

    def update(self, index, active_layers=(), caps_lock=False):
        if type(index) is not int or not (0 <= index < self.units):
            raise IndexError('unit out of range')
        frame = self.policy.render(active_layers, caps_lock)
        if self.synchronized:
            self._frames = [frame for _ in range(self.units)]
        else:
            self._frames[index] = frame
        return self.snapshot()

    def snapshot(self):
        return tuple(self._frames)


class RGBHardwareUnavailable(RuntimeError):
    pass


def open_rgb_hardware(*_args, **_kwargs):
    """Fail closed: no guessed HID protocol and no automatic firmware flashing."""
    raise RGBHardwareUnavailable('No verified Windows RGB protocol for this keyboard; preview only')
