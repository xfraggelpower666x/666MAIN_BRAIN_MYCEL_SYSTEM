"""Explicit capability boundary for future device-specific keyboard LED adapters.

A Windows lock-key toggle is NOT a device-specific HID LED write. Never claim
USB keyboard isolation without a verified backend and hardware acceptance.
"""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class KeyboardLedCapability:
    device_id: str
    leds: tuple[str, ...] = ()
    independent_of_lock_state: bool = False
    verified: bool = False
    reason: str = 'No verified device-specific HID LED backend installed'

class IndependentLedBackend(Protocol):
    def capabilities(self) -> KeyboardLedCapability: ...
    def set_led(self, name: str, enabled: bool) -> None: ...
    def close(self) -> None: ...

class UnsupportedHidBackend:
    """Fail closed; never turn this into a success-returning hardware stub."""
    def capabilities(self) -> KeyboardLedCapability:
        return KeyboardLedCapability(device_id='unavailable')

    def set_led(self, name: str, enabled: bool) -> None:
        raise RuntimeError('No verified, per-device HID LED transport; hardware remains off')

    def close(self) -> None:
        return None
