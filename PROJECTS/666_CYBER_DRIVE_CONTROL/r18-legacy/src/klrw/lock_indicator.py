"""Virtual lock indicators with configurable ordering and state-change events.

A Windows lock-key state does NOT prove that a physical keyboard LED is lit.
This module is read-only; hardware toggling is provided separately by ledctl.
"""
from dataclasses import dataclass
import sys
from .model import LEDS
from .leds import VK

LETTERS = {"num": "N", "caps": "C", "scroll": "S"}
REVERSE = {value: key for key, value in LETTERS.items()}


def parse_order(order: str) -> tuple[str, ...]:
    if not isinstance(order, str) or len(order) > 3 or any(x not in REVERSE for x in order):
        raise ValueError("order must contain only N, C, S (no repeats)")
    if len(set(order)) != len(order):
        raise ValueError("duplicate LED in order")
    return tuple(REVERSE[x] for x in order)


@dataclass(frozen=True)
class LockSnapshot:
    caps: bool
    num: bool
    scroll: bool

    def as_dict(self):
        return {led: bool(getattr(self, led)) for led in LEDS}


class WindowsLockReader:
    """Read Windows lock state without simulating keys or requiring elevation."""
    def __init__(self, user32=None):
        if user32 is None:
            if sys.platform != "win32":
                raise OSError("Windows lock state requires Windows")
            import ctypes
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.GetKeyState.argtypes = [ctypes.c_int]
            user32.GetKeyState.restype = ctypes.c_short
        self.user32 = user32

    def read(self) -> LockSnapshot:
        values = {led: bool(self.user32.GetKeyState(VK[led]) & 1) for led in LEDS}
        return LockSnapshot(**values)


class PreviewLockReader:
    def __init__(self, caps=False, num=False, scroll=False):
        self.snapshot = LockSnapshot(caps, num, scroll)

    def read(self):
        return self.snapshot


class LockIndicator:
    """Only emits changes; display ordering and hiding are presentation-only."""
    def __init__(self, reader, order="NCS"):
        self.reader = reader
        self.order = parse_order(order)
        self.last = None

    def poll(self):
        snapshot = self.reader.read()
        if not isinstance(snapshot, LockSnapshot):
            raise TypeError("reader must return LockSnapshot")
        ordered = tuple((led, getattr(snapshot, led)) for led in self.order)
        if ordered == self.last:
            return None
        self.last = ordered
        return ordered

    def set_order(self, order):
        self.order = parse_order(order)
        self.last = None


def display_text(ordered):
    return "   ".join(f"{LETTERS[led]} {'●' if enabled else '○'}" for led, enabled in ordered) or "Keine Lock-Anzeigen"
