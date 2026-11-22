"""Single-owner interlock for risky GLOBAL Caps/Num/Scroll writes.

No write happens here. Ownership is released by each owning controller when its
backend/monitor stops. It prevents concurrent UI facets fighting over lock keys.
"""
from threading import RLock

_mutex=RLock()
_owner=None


def claim(owner):
    global _owner
    with _mutex:
        if _owner is not None and _owner != owner:
            raise RuntimeError('Globale Lock-Tasten-Steuerung läuft bereits in einem anderen Bereich.')
        _owner=owner


def release(owner):
    global _owner
    with _mutex:
        if _owner==owner:
            _owner=None


def current_owner():
    with _mutex:
        return _owner
