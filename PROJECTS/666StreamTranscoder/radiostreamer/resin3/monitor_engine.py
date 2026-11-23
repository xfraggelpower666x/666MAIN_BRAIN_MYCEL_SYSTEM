"""Independent local audio monitor. Stopping it never touches the relay session."""
import queue
import threading


class LocalMonitor:
    @staticmethod
    def list_output_devices():
        try:
            import sounddevice as sd
            return sorted({str(device["name"]) for device in sd.query_devices()
                           if int(device.get("max_output_channels", 0)) > 0})
        except Exception:
            return []

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

            device_index = None
            if self.device != "Default output":
                for index, info in enumerate(sd.query_devices()):
                    if info["name"] == self.device and int(info.get("max_output_channels", 0)) >= self.channels:
                        device_index = index
                        break
                if device_index is None:
                    raise RuntimeError(f"Monitor output device not available: {self.device}")
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
