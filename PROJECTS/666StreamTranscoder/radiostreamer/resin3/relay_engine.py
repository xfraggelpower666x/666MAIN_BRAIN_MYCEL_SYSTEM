"""Lifecycle facade keeping relay output and local monitoring independent."""
from .status_bus import StatusBus
from .monitor_engine import LocalMonitor
from .control_plane import ConnectionWatch, ReconnectPolicy
import time
import threading


class RelayController:
    """Owns relay connection state, reconnect backoff and byte-activity monitoring."""
    def __init__(self, cfg, output_engine):
        self.cfg = dict(cfg)
        self.output = output_engine
        self.watch = ConnectionWatch()
        self.policy = ReconnectPolicy(cfg.get("reconnect_delay", 5), cfg.get("max_retries", 0))
        self._retry_at = 0.0
        self.sock = None
        self.lock = threading.Lock()

    def connecting(self, target):
        self.watch.connecting(target)

    def open(self):
        return self.output.open()

    def attach(self, sock):
        with self.lock:
            self.sock = sock

    def current(self):
        with self.lock:
            return self.sock

    def send(self, encoded_bytes):
        with self.lock:
            if self.sock is None:
                return 0
            sent = self.output.send(self.sock, encoded_bytes)
            self.watch.sent(sent)
            return sent

    def close(self, reason=""):
        with self.lock:
            sock, self.sock = self.sock, None
            retry = self.disconnected(reason or "")
        if sock is not None:
            self.output.close(sock)
        return sock is not None, retry

    def connected(self, target):
        self.policy.connected()
        self._retry_at = 0.0
        self.watch.connected(target)

    def failed(self, reason):
        return self.disconnected(reason)

    def wait_remaining(self):
        return max(0.0, self._retry_at - time.monotonic())

    def sent(self, byte_count):
        self.watch.sent(byte_count)

    def disconnected(self, reason=""):
        self.watch.disconnected(reason)
        if reason:
            result = self.policy.failed()
            self._retry_at = time.monotonic() + result[1]
            return result
        return None

    def snapshot(self):
        return self.watch.snapshot()


class RelaySession:
    def __init__(self, broadcaster, status_bus=None, monitor=None):
        self.broadcaster = broadcaster
        self.status = status_bus or StatusBus()
        self.monitor = monitor or LocalMonitor(
            samplerate=broadcaster.sr, channels=broadcaster.ch
        )
        self.broadcaster.monitor_sink = self.monitor

    def start(self):
        self.broadcaster.start()
        self.status.publish("relay", "starting", "Broadcast engine started.")

    def stop_monitor(self):
        self.monitor.stop()
        self.status.publish("monitor", "stopped", "Local monitor stopped; relay remains active.")

    def start_monitor(self):
        self.monitor.start()
        self.status.publish("monitor", "running", "Local monitor active.")

    def set_monitor_volume(self, value):
        self.monitor.set_volume(value)
        self.status.publish("monitor", "muted" if float(value) <= 0 else "running",
                            f"Local monitor volume: {self.monitor.volume:.2f}")

    def disconnect(self):
        self.monitor.stop()
        self.broadcaster.stop()
        self.status.publish("relay", "disconnected", "Radio output disconnected.")
