"""Independent local audio monitor. Stopping it never touches the relay session."""
import queue
import threading
import re


class LocalMonitor:
    # Index is scoped to a specific PortAudio enumeration. Host/name are
    # rechecked before opening so stale indices cannot silently route audio.
    DEVICE_LABEL = re.compile(r"^PA:(\\d+) \\| ([^|]+) \\| (.+)$")

    @staticmethod
    def _inventory(sd):
        devices = sd.query_devices()
        apis = sd.query_hostapis()
        records = []
        for index, device in enumerate(devices):
            if int(device.get("max_output_channels", 0)) <= 0:
                continue
            host_index = int(device.get("hostapi", 0))
            host_name = str(apis[host_index]["name"]) if 0 <= host_index < len(apis) else "Unknown API"
            label = f'PA:{index} | {host_name} | {device["name"]}'
            records.append((index, str(device["name"]), host_name, label,
                            int(device.get("max_output_channels", 0))))
        return records

    @classmethod
    def list_output_devices(cls):
        try:
            import sounddevice as sd
            return [record[3] for record in cls._inventory(sd)]
        except Exception:
            return []

    @classmethod
    def resolve_output_device(cls, sd, selected, channels):
        if not selected or selected == "Default output":
            return None
        records = cls._inventory(sd)
        match = cls.DEVICE_LABEL.fullmatch(str(selected))
        if match:
            index, host_name, name = int(match.group(1)), match.group(2), match.group(3)
            candidates = [record for record in records
                          if record[0] == index and record[1] == name
                          and record[2] == host_name and record[4] >= channels]
            if len(candidates) != 1:
                raise RuntimeError("Selected monitor endpoint changed; refresh device list and select again.")
            return candidates[0][0]
        # Existing saved plain-name settings remain supported when unambiguous.
        candidates = [record for record in records if record[1] == selected and record[4] >= channels]
        if len(candidates) == 1:
            return candidates[0][0]
        if len(candidates) > 1:
            raise RuntimeError("Multiple audio devices share this name; refresh and select a PA endpoint.")
        raise RuntimeError(f"Monitor output device not available: {selected}")

    def __init__(self, samplerate=44100, channels=2, volume=1.0, blocksize=1024, device="Default output"):
        self.samplerate = int(samplerate)
        self.channels = int(channels)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.blocksize = int(blocksize)
        self.device = str(device or "Default output")
        self._queue = queue.Queue(maxsize=32)
        self._stream = None
        self._lock = threading.RLock()
        self._muted = False
        self._pending = bytearray()

    @property
    def running(self):
        return self._stream is not None

    def start(self):
        with self._lock:
            if self._stream is not None:
                return
            try:
                import sounddevice as sd
            except ImportError as exc:
                raise RuntimeError("Local monitor requires the optional 'sounddevice' package.") from exc

            def callback(outdata, frames, time_info, status):
                needed_bytes = frames * self.channels * 2
                while len(self._pending) < needed_bytes:
                    try:
                        self._pending.extend(self._queue.get_nowait())
                    except queue.Empty:
                        break
                if len(self._pending) < needed_bytes:
                    outdata.fill(0)
                    return
                data = bytes(self._pending[:needed_bytes])
                del self._pending[:needed_bytes]
                if self._muted or self.volume <= 0:
                    outdata.fill(0)
                    return
                import numpy as np
                samples = np.frombuffer(data, dtype=np.int16)
                outdata[:] = (samples.reshape(frames, self.channels).astype(np.float32)
                              * (self.volume / 32768.0))

            device_index = self.resolve_output_device(sd, self.device, self.channels)
            stream = sd.OutputStream(device=device_index, samplerate=self.samplerate, channels=self.channels,
                                     dtype="float32", blocksize=self.blocksize, callback=callback)
            try:
                stream.start()
            except Exception:
                stream.close()
                raise
            self._stream = stream

    def write(self, pcm_s16le):
        if not self.running or self._muted:
            return
        try:
            self._queue.put_nowait(bytes(pcm_s16le))
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(bytes(pcm_s16le))
            except queue.Full:
                pass

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, float(value)))

    def mute(self, muted=True):
        self._muted = bool(muted)

    def stop(self):
        """Stop only the local monitor device; do not disconnect or stop the radio relay."""
        with self._lock:
            stream, self._stream = self._stream, None
            if stream is not None:
                try:
                    stream.stop()
                except Exception:
                    pass
                stream.close()
            self._pending.clear()
            while True:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
