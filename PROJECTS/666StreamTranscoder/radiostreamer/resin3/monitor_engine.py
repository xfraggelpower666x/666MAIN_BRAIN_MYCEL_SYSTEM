"""Independent local audio monitor. Stopping it never touches the relay session."""
import queue
import threading


class LocalMonitor:
    def __init__(self, samplerate=44100, channels=2, volume=1.0, blocksize=1024):
        self.samplerate = int(samplerate)
        self.channels = int(channels)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.blocksize = int(blocksize)
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

            self._stream = sd.OutputStream(samplerate=self.samplerate, channels=self.channels,
                                           dtype="float32", blocksize=self.blocksize, callback=callback)
            self._stream.start()

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
                stream.stop()
                stream.close()
            self._pending.clear()
            while True:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
