"""Manual LED diagnostic derived from interface ideas, not macOS implementation.

No auto hardware activation, no macOS tool, no hidden persistent state.
"""
from dataclasses import dataclass
from .leds import PreviewBackend, WindowsLockBackend
from .model import LEDS

@dataclass(frozen=True)
class LedResult:
    led: str
    state: bool
    source: str

class ManualLedController:
    """One-shot LED state/set bridge, with explicit hardware opt-in.

    Windows lock key LEDs are *not* independent LED devices. A set operation
    changes the associated functional key state; hardware can ignore it.
    """
    def __init__(self, hardware=False, backend=None):
        self.hardware = bool(hardware)
        self.backend = backend if backend is not None else (WindowsLockBackend() if hardware else PreviewBackend())
        self.closed = False

    def state(self, led):
        if led not in LEDS:
            raise ValueError("unknown LED")
        if self.closed:
            raise RuntimeError("controller closed")
        if self.hardware:
            if not hasattr(self.backend, '_read'):
                raise RuntimeError("hardware backend cannot read state")
            value = self.backend._read(led)
        else:
            value = self.backend.states[led]
        return LedResult(led, bool(value), 'windows-lock-state' if self.hardware else 'preview')

    def set(self, led, value):
        if type(value) is not bool:
            raise ValueError("state must be true or false")
        if led not in LEDS:
            raise ValueError("unknown LED")
        if self.closed:
            raise RuntimeError("controller closed")
        self.backend.apply(led, value)
        return self.state(led)

    def close(self):
        if not self.closed:
            self.closed = True
            self.backend.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
