"""LED backends. Win32 toggles LOCK KEY STATE, not isolated LED hardware.

Important: Caps/Num/Scroll are functional keys. The adapter does not promise
independent LED control or reliable support on every keyboard.
"""
import sys
import threading
from .model import LEDS

VK = {"caps": 0x14, "num": 0x90, "scroll": 0x91}

class PreviewBackend:
    def __init__(self):
        self.states = {led: False for led in LEDS}
    def apply(self, led: str, value: bool):
        self.states[led] = bool(value)
    def close(self):
        self.states = {led: False for led in LEDS}

class WindowsLockBackend:
    """Best-effort restore of initial lock-key states upon normal shutdown.

    User manual key changes during runtime cannot be distinguished reliably.
    Use only after explicit opt-in. No keyboard model is guaranteed to work.
    """
    def __init__(self):
        if sys.platform != "win32":
            raise OSError("Hardware backend requires native Windows")
        import ctypes
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetKeyState.argtypes = [ctypes.c_int]
        self.user32.GetKeyState.restype = ctypes.c_short
        self.user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ulong, ctypes.c_size_t]
        self.user32.keybd_event.restype = None
        self.lock = threading.RLock()
        self.original = {led: self._read(led) for led in LEDS}
        self.touched = set()
        self.closed = False

    def _read(self, led):
        return bool(self.user32.GetKeyState(VK[led]) & 1)

    def _toggle(self, led):
        vk = VK[led]
        self.user32.keybd_event(vk, 0, 0, 0)
        self.user32.keybd_event(vk, 0, 0x0002, 0)

    def apply(self, led: str, value: bool):
        if led not in VK:
            raise ValueError("unknown LED")
        with self.lock:
            if self.closed:
                raise RuntimeError("backend closed")
            if self._read(led) != bool(value):
                self._toggle(led)
                self.touched.add(led)

    def close(self):
        with self.lock:
            if self.closed:
                return
            self.closed = True
            for led in self.touched:
                if self._read(led) != self.original[led]:
                    self._toggle(led)
