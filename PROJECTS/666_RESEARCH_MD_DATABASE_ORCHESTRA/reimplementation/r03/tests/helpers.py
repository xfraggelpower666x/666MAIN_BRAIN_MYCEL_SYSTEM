from __future__ import annotations
import tempfile
import wave
import unittest
from pathlib import Path
import numpy as np
from src import stem_masking as analyzer

def write_wav(path: Path, *, frequency: float = 1000.0, duration: float = 1.0,
              sample_rate: int = 48000, channels: int = 1, width: int = 2,
              amplitude: float = 0.5, inverted_right: bool = False,
              silence: bool = False) -> None:
    frames = int(sample_rate * duration)
    t = np.arange(frames, dtype=np.float64) / sample_rate
    signal = np.zeros(frames, dtype=np.float64) if silence else amplitude * np.sin(2 * np.pi * frequency * t)
    data = np.column_stack((signal, -signal if inverted_right else signal)) if channels == 2 else signal[:, None]
    if width == 1:
        encoded = np.clip(np.rint(data * 128.0 + 128.0), 0, 255).astype(np.uint8).tobytes()
    elif width == 2:
        encoded = np.clip(np.rint(data * 32768.0), -32768, 32767).astype("<i2").tobytes()
    elif width == 3:
        ints = np.clip(np.rint(data * 8388608.0), -8388608, 8388607).astype(np.int32).reshape(-1)
        unsigned = ints & 0xFFFFFF
        packed = np.empty((len(unsigned), 3), dtype=np.uint8)
        packed[:, 0] = unsigned & 0xFF
        packed[:, 1] = (unsigned >> 8) & 0xFF
        packed[:, 2] = (unsigned >> 16) & 0xFF
        encoded = packed.tobytes()
    elif width == 4:
        encoded = np.clip(np.rint(data * 2147483648.0), -2147483648, 2147483647).astype("<i4").tobytes()
    else:
        raise ValueError(width)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(channels); out.setsampwidth(width); out.setframerate(sample_rate); out.writeframes(encoded)

class R03TestBase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ro-r03-")
        self.root = Path(self.temp.name) / "input"; self.root.mkdir()
    def tearDown(self): self.temp.cleanup()
    def stem(self, role, **kwargs):
        filename = f"{role}.wav"; write_wav(self.root / filename, **kwargs); return role, filename
    def analyze(self, *specs): return analyzer.analyze_stems(self.root, list(specs))

