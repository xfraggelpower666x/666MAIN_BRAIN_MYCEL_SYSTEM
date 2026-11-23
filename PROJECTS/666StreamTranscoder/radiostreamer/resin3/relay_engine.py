"""Lifecycle facade keeping relay output and local monitoring independent."""
from .status_bus import StatusBus
from .monitor_engine import LocalMonitor


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
