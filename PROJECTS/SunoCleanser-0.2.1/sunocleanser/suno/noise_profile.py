from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def linked_magnitude(magnitudes: Sequence[np.ndarray]) -> np.ndarray:
    """Channel-linked magnitude: mean over all channels (mono input passes through)."""
    return np.mean(np.stack(list(magnitudes), axis=0), axis=0)


def frame_quiet_scores(
    magnitudes: Sequence[np.ndarray],
    freqs: np.ndarray,
    bass_cut_hz: float = 350.0,
) -> np.ndarray:
    """
    Per-frame energy from channel-linked magnitudes, ignoring bins below bass_cut_hz
    so kick/bass do not dominate quiet-frame selection.
    """
    mono_mag = linked_magnitude(magnitudes)
    bass_mask = freqs < bass_cut_hz
    if np.all(bass_mask):
        band_mag = mono_mag
    else:
        band_mag = mono_mag[~bass_mask, :]
    return np.mean(band_mag**2, axis=0)


def estimate_noise_spectrum(
    magnitudes: Sequence[np.ndarray],
    freqs: np.ndarray,
    quiet_fraction: float = 0.12,
    bass_cut_hz: float = 350.0,
) -> tuple[np.ndarray, int]:
    """
    Average magnitude spectrum over the quietest fraction of frames (linked channels).
    Returns noise profile (freq_bins,) and count of frames used.
    """
    scores = frame_quiet_scores(magnitudes, freqs, bass_cut_hz)
    n_frames = scores.shape[0]
    n_quiet = min(n_frames, max(1, int(np.ceil(n_frames * quiet_fraction))))
    quiet_idx = np.argpartition(scores, n_quiet - 1)[:n_quiet]
    mono_mag = linked_magnitude(magnitudes)
    noise_profile = np.mean(mono_mag[:, quiet_idx], axis=1)
    noise_floor = np.max(noise_profile) * 1e-6 + 1e-12
    noise_profile = np.maximum(noise_profile, noise_floor)
    return noise_profile, n_quiet
