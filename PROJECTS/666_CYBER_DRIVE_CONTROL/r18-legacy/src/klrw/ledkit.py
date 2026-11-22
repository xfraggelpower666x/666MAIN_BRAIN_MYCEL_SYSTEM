"""Device-neutral, capability-aware LED kit (independent implementation).

Inspired by the object-oriented interface of jwilk-archive/python-keyboardleds
(MIT), without incorporating its Linux ioctl/evdev implementation.

A Windows lock-key backend changes the FUNCTIONAL LOCK STATE and must never be
advertised as independent control of a physical indicator. No automatic writes.
"""
from dataclasses import dataclass
from threading import RLock
from .model import LEDS
from .leds import PreviewBackend, WindowsLockBackend


@dataclass(frozen=True)
class Capabilities:
    read: bool = True
    write: bool = True
    independent_physical_led: bool = False
    changes_functional_lock_state: bool = False


class UnsupportedOperation(RuntimeError):
    pass


class LedKit:
    """Preserve per-LED state and provide transactional group operations.

    By default, hardware mode is disabled. Hardware mode must be explicitly
    requested. An adapter can supply `read(name)`, `apply(name, bool)` and
    `close()` and optionally advertise `capabilities`.
    """
    def __init__(self, hardware=False, backend=None, capabilities=None):
        self.hardware = bool(hardware)
        self.backend = backend if backend is not None else (
            WindowsLockBackend() if hardware else PreviewBackend()
        )
        self.capabilities = capabilities or Capabilities(
            changes_functional_lock_state=self.hardware
        )
        self._lock = RLock()
        self.closed = False
        self.caps = Light(self, 'caps')
        self.num = Light(self, 'num')
        self.scroll = Light(self, 'scroll')

    def _check(self, name, write=False):
        if name not in LEDS:
            raise ValueError('unknown LED')
        if self.closed:
            raise RuntimeError('kit closed')
        if write and not self.capabilities.write:
            raise UnsupportedOperation('backend is read-only')
        if not write and not self.capabilities.read:
            raise UnsupportedOperation('backend cannot read state')

    def read(self, name):
        with self._lock:
            self._check(name)
            if hasattr(self.backend, 'read'):
                return bool(self.backend.read(name))
            if self.hardware and hasattr(self.backend, '_read'):
                return bool(self.backend._read(name))
            if hasattr(self.backend, 'states'):
                return bool(self.backend.states[name])
            raise UnsupportedOperation('backend has no readable LED state')

    def snapshot(self):
        with self._lock:
            return {name: self.read(name) for name in LEDS}

    def set(self, name, enabled):
        if type(enabled) is not bool:
            raise ValueError('LED state must be boolean')
        with self._lock:
            self._check(name, write=True)
            self.backend.apply(name, enabled)

    def toggle(self, name):
        with self._lock:
            self._check(name, write=True)
            return self._set_and_read(name, not self.read(name))

    def _set_and_read(self, name, enabled):
        self.set(name, enabled)
        return self.read(name)

    def set_many(self, values):
        """Apply a subset atomically as far as backend semantics permit.

        On a failure, restore already modified keys in reverse order. If
        recovery also fails, raise an ExceptionGroup so no failure is hidden.
        This is best-effort, NOT a hardware transaction guarantee.
        """
        values = dict(values)
        if any(name not in LEDS for name in values):
            raise ValueError('unknown LED')
        if any(type(value) is not bool for value in values.values()):
            raise ValueError('LED state must be boolean')
        with self._lock:
            if not values:
                return self.snapshot()
            for name in values:
                self._check(name, write=True)
            previous = {name: self.read(name) for name in values}
            changed = []
            try:
                for name, enabled in values.items():
                    if previous[name] != enabled:
                        changed.append(name)
                        self.set(name, enabled)
            except Exception as exc:
                recovery = []
                for name in reversed(changed):
                    try:
                        self.set(name, previous[name])
                    except Exception as err:
                        recovery.append(err)
                if recovery:
                    raise ExceptionGroup('LED write and rollback both failed', [exc, *recovery]) from exc
                raise
            return self.snapshot()

    def close(self):
        with self._lock:
            if not self.closed:
                self.closed = True
                self.backend.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class Light:
    """Per-LED facade without cross-device or global state."""
    def __init__(self, kit, name):
        self.kit = kit
        self.name = name

    def get(self):
        return self.kit.read(self.name)

    def set(self):
        self.kit.set(self.name, True)

    def reset(self):
        self.kit.set(self.name, False)

    def toggle(self):
        return self.kit.toggle(self.name)
