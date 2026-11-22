"""Pure status projection for the optional Windows tray (no hardware writes)."""
from dataclasses import dataclass
from .lock_indicator import LockSnapshot, parse_order

@dataclass(frozen=True)
class TrayFrame:
    order: tuple[str, ...]
    enabled: tuple[bool, ...]
    label: str
    fingerprint: tuple


def make_frame(snapshot: LockSnapshot, order: str = "NCS") -> TrayFrame:
    if not isinstance(snapshot, LockSnapshot):
        raise TypeError("snapshot must be LockSnapshot")
    keys = parse_order(order)
    enabled = tuple(bool(getattr(snapshot, key)) for key in keys)
    labels = {"num": "NUM", "caps": "CAPS", "scroll": "SCRL"}
    label = " | ".join(f"{labels[k]}: {'ON' if v else 'OFF'}" for k, v in zip(keys, enabled))
    return TrayFrame(keys, enabled, label or "No indicators selected", (keys, enabled))


class ChangeGate:
    """Suppress redraws when monitored states are unchanged."""
    def __init__(self):
        self._last = None

    def accept(self, frame: TrayFrame) -> bool:
        if not isinstance(frame, TrayFrame):
            raise TypeError("frame must be TrayFrame")
        if frame.fingerprint == self._last:
            return False
        self._last = frame.fingerprint
        return True
