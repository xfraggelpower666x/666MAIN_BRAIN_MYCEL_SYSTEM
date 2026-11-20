from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass(frozen=True)
class WavInfo:
    sample_rate: int
    channels: int
    subtype: str
    frames: int


def load_audio(path: Path) -> tuple[np.ndarray, WavInfo]:
    """Load a soundfile-supported audio file as float64, preserving channels."""
    data, sample_rate = sf.read(path, dtype="float64", always_2d=True)
    with sf.SoundFile(path) as f:
        info = WavInfo(
            sample_rate=int(sample_rate),
            channels=int(f.channels),
            subtype=str(f.subtype),
            frames=len(f),
        )
    return data, info


def load_wav(path: Path) -> tuple[np.ndarray, WavInfo]:
    """Backward-compatible alias for loading audio files."""
    return load_audio(path)


def write_wav_24bit(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    """Write PCM_24 WAV without normalization (values beyond +-1.0 are clipped by the format)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sample_rate, subtype="PCM_24")


def peak_levels(audio: np.ndarray) -> dict[str, object]:
    """Per-channel peaks. peak_l/peak_r are kept for report compatibility."""
    peaks = np.max(np.abs(audio), axis=0)
    per_channel = [float(p) for p in peaks]
    return {
        "peak_l": per_channel[0],
        "peak_r": per_channel[1] if len(per_channel) > 1 else per_channel[0],
        "per_channel": per_channel,
    }


def count_clipped(audio: np.ndarray) -> int:
    """Number of samples whose magnitude exceeds full scale (lost in a PCM write)."""
    return int(np.count_nonzero(np.abs(audio) > 1.0))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()
