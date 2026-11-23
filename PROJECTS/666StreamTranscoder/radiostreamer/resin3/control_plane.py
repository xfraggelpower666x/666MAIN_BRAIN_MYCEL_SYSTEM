"""Resin 3 signal control plane: independent stream gain, metering and route description."""
import array
import math
import re
import threading

try:
    import audioop
except ImportError:
    audioop = None


class GainStage:
    """Thread-safe post-mix stream gain. Local monitor is tapped before this stage."""
    def __init__(self, percent=100):
        self._lock = threading.Lock()
        self._gain = self._clamp(percent)

    @staticmethod
    def _clamp(value):
        return max(0.0, min(2.0, float(value) / 100.0))

    @property
    def gain(self):
        with self._lock:
            return self._gain

    def set_percent(self, value):
        with self._lock:
            self._gain = self._clamp(value)
            return self._gain

    def process(self, pcm_s16le):
        with self._lock:
            gain = self._gain
        if gain == 1.0:
            return pcm_s16le
        if audioop:
            return audioop.mul(pcm_s16le, 2, gain)
        samples = array.array("h", pcm_s16le)
        for i, sample in enumerate(samples):
            samples[i] = max(-32768, min(32767, int(sample * gain)))
        return samples.tobytes()


def peak_dbfs(pcm_s16le):
    """Peak level of interleaved signed 16-bit PCM, in dBFS."""
    if not pcm_s16le:
        return -120.0
    samples = array.array("h", pcm_s16le[:len(pcm_s16le) // 2 * 2])
    if not samples:
        return -120.0
    peak = max(abs(value) for value in samples)
    if peak == 0:
        return -120.0
    return max(-120.0, 20.0 * math.log10(peak / 32768.0))


class RoutePlan:
    """Human-readable route description without changing native source/output authority."""
    INPUTS = {
        "queue": "playlist decoder",
        "device": "audio input / virtual cable capture",
        "loopback": "WASAPI system loopback",
        "app": "WASAPI process loopback",
        "relay": "HTTP(S) radio relay input",
    }

    @staticmethod
    def output(server_type):
        if server_type == "Built-in (this PC)":
            return "built-in Icecast-compatible listener server"
        if server_type == "Icecast 2":
            return "Icecast 2 source output"
        if str(server_type).startswith("Shoutcast"):
            return "Shoutcast source output"
        return "unconfigured output"

    @classmethod
    def describe(cls, source, server_type, monitor_device=""):
        return {
            "input": cls.INPUTS.get(source, "unknown input"),
            "output": cls.output(server_type),
            "monitor": monitor_device or "default local output",
        }

    @staticmethod
    def validate_monitor_route(source, input_device="", monitor_device=""):
        """Fail closed for a looped-back virtual cable; warn on unresolved WASAPI endpoints."""
        source = str(source or "").lower()
        input_device = str(input_device or "").lower()
        monitor_device = str(monitor_device or "").lower()
        cable = re.compile(r"\\bcable[- ]?([a-d])?\\s+(input|output)\\b")
        capture = cable.search(input_device)
        playback = cable.search(monitor_device)
        if source == "device" and capture and playback:
            # Standard VB-CABLE (no suffix) and A/B/C/D cables must not
            # feed their own playback input from their corresponding capture.
            same_cable = capture.group(1) == playback.group(1)
            if capture.group(2) == "output" and playback.group(2) == "input" and same_cable:
                raise ValueError(
                    "Monitor cannot play to CABLE Input while CABLE Output is the stream source: "
                    "this creates an audio feedback loop. Pick a physical monitor output."
                )
        if source == "loopback":
            return ("Verify that local monitoring does not feed the captured WASAPI "
                    "endpoint; exact Windows endpoint identity requires host validation.")
        return ""


class ConnectionWatch:
    """Live output health counters consumed by the UI and diagnostics."""
    def __init__(self):
        self._lock = threading.Lock()
        self.state = "idle"
        self.target = ""
        self.connected_at = None
        self.last_activity = None
        self.last_error = ""
        self.bytes_sent = 0

    def connecting(self, target):
        with self._lock:
            self.state, self.target = "connecting", str(target)

    def connected(self, target):
        import time
        with self._lock:
            self.state, self.target = "connected", str(target)
            self.connected_at = time.time()
            self.last_activity = self.connected_at
            self.last_error = ""

    def sent(self, byte_count):
        import time
        with self._lock:
            self.bytes_sent += int(byte_count)
            self.last_activity = time.time()

    def disconnected(self, reason=""):
        with self._lock:
            self.state = "retrying" if reason else "disconnected"
            self.last_error = str(reason or "")

    def snapshot(self):
        with self._lock:
            return {
                "state": self.state, "target": self.target, "connected_at": self.connected_at,
                "last_activity": self.last_activity, "last_error": self.last_error,
                "bytes_sent": self.bytes_sent,
            }


class ReconnectPolicy:
    """Bounded exponential reconnect delay with the existing 0=unlimited retry contract."""
    def __init__(self, base_delay=5, max_retries=0, cap=60):
        self.base_delay = max(1, int(base_delay))
        self.max_retries = max(0, int(max_retries))
        self.cap = max(self.base_delay, int(cap))
        self.attempts = 0

    def failed(self):
        self.attempts += 1
        delay = min(self.cap, self.base_delay * (2 ** min(self.attempts - 1, 10)))
        exhausted = bool(self.max_retries and self.attempts >= self.max_retries)
        return self.attempts, delay, exhausted

    def connected(self):
        self.attempts = 0
