"""Thread-safe status/event bus shared by source, monitor, encoder and output modules."""
from dataclasses import dataclass
from datetime import datetime, timezone
import threading


@dataclass(frozen=True)
class StatusEvent:
    component: str
    state: str
    message: str = ""
    timestamp: str = ""


class StatusBus:
    def __init__(self):
        self._lock = threading.RLock()
        self._listeners = set()
        self._latest = {}

    def subscribe(self, callback):
        with self._lock:
            self._listeners.add(callback)
        return lambda: self.unsubscribe(callback)

    def unsubscribe(self, callback):
        with self._lock:
            self._listeners.discard(callback)

    def publish(self, component, state, message=""):
        event = StatusEvent(component, state, message,
                            datetime.now(timezone.utc).isoformat())
        with self._lock:
            self._latest[component] = event
            listeners = tuple(self._listeners)
        for callback in listeners:
            try:
                callback(event)
            except Exception:
                # A UI/status consumer must not break the audio runtime.
                continue
        return event

    def snapshot(self):
        with self._lock:
            return dict(self._latest)
