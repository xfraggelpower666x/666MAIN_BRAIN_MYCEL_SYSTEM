from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, TypedDict

import numpy as np
from scipy import signal

from sunocleanser import __version__
from sunocleanser.audio.io import (
    count_clipped,
    load_audio,
    load_wav,
    peak_levels,
    sha256_file,
    write_wav_24bit,
)
from sunocleanser.audio.stft import (
    StftConfig,
    align_length,
    istft_channel,
    stft_channel,
)
from sunocleanser.suno.gain_mask import (
    MAX_ATTENUATION_DB,
    apply_gain_to_spectrum,
    raw_gain_mask,
    smooth_gain_mask,
)
from sunocleanser.suno.noise_profile import estimate_noise_spectrum, linked_magnitude


class InvalidInputError(ValueError):
    """Input file or parameters cannot be processed (user-fixable)."""


@dataclass(frozen=True)
class ProcessingParams:
    n_fft: int = 2048
    hop_length: int = 512
    window: str = "hann"
    quiet_fraction: float = 0.12
    bass_cut_hz: float = 350.0
    oversubtraction: float = 1.2
    freq_smooth_sigma: float = 1.5
    time_smooth_sigma: float = 1.0
    reconstruction_threshold_db: float = -60.0

    def __post_init__(self) -> None:
        for name in (
            "quiet_fraction",
            "bass_cut_hz",
            "oversubtraction",
            "freq_smooth_sigma",
            "time_smooth_sigma",
            "reconstruction_threshold_db",
        ):
            value = getattr(self, name)
            if not math.isfinite(value):
                raise InvalidInputError(f"{name} must be finite (got {value}).")
        if self.n_fft < 64:
            raise InvalidInputError(f"n_fft must be >= 64 (got {self.n_fft}).")
        if not 1 <= self.hop_length < self.n_fft:
            raise InvalidInputError(
                f"hop_length must satisfy 1 <= hop < n_fft (got hop={self.hop_length}, n_fft={self.n_fft})."
            )
        if not 0.0 < self.quiet_fraction <= 1.0:
            raise InvalidInputError(f"quiet_fraction must be in (0, 1] (got {self.quiet_fraction}).")
        if self.bass_cut_hz < 0 or self.oversubtraction < 0:
            raise InvalidInputError("bass_cut_hz and oversubtraction must be >= 0.")
        if self.freq_smooth_sigma < 0 or self.time_smooth_sigma < 0:
            raise InvalidInputError("Smoothing sigmas must be >= 0.")
        try:
            window = signal.get_window(self.window, self.n_fft)
        except ValueError as exc:
            raise InvalidInputError(f"Invalid window '{self.window}': {exc}") from exc
        if not signal.check_NOLA(window, self.n_fft, self.n_fft - self.hop_length):
            raise InvalidInputError(
                "Window/hop combination does not satisfy NOLA (perfect reconstruction impossible)."
            )


@dataclass
class ProcessingResult:
    clean_path: Path
    noise_path: Path
    report: dict


class NullTestMetrics(TypedDict):
    max_abs_error: float
    rms_error: float
    max_error_db: float
    rms_error_db: float
    reference: Literal["full_scale_dbfs"]


def null_test_error(
    original: np.ndarray,
    noise_readback: np.ndarray,
    clean_readback: np.ndarray,
) -> NullTestMetrics:
    """
    Real phase-cancel check on the *written* 24-bit files:
    original + inverted(noise) must equal clean. Errors are reported in dBFS
    (full scale = 1.0), exactly as a DAW null test would show them.
    """
    diff = (original - noise_readback) - clean_readback
    max_abs = float(np.max(np.abs(diff)))
    rms = float(np.sqrt(np.mean(diff**2)))
    return {
        "max_abs_error": max_abs,
        "rms_error": rms,
        "max_error_db": float(20.0 * np.log10(max_abs + 1e-15)),
        "rms_error_db": float(20.0 * np.log10(rms + 1e-15)),
        "reference": "full_scale_dbfs",
    }


def _validate_audio(original: np.ndarray, params: ProcessingParams) -> None:
    n_frames = original.shape[0]
    if n_frames == 0:
        raise InvalidInputError("Input audio contains no samples.")
    if n_frames < params.n_fft:
        raise InvalidInputError(
            f"Input too short: {n_frames} samples, need at least n_fft={params.n_fft}."
        )
    if not np.all(np.isfinite(original)):
        raise InvalidInputError("Input audio contains NaN/Inf samples.")


def wav_output_paths(
    input_path: Path, out_dir: Path | None, title: str | None
) -> tuple[Path, Path]:
    destination = out_dir if out_dir is not None else input_path.parent
    song_title = title or input_path.stem
    has_path_syntax = "/" in song_title or "\\" in song_title
    song_title = song_title.replace("/", "_").replace("\\", "_")
    if has_path_syntax or (
        len(song_title) > 1
        and song_title[0].isascii()
        and song_title[0].isalpha()
        and song_title[1] == ":"
    ):
        song_title = song_title.replace(":", "_")
    return (
        destination / f"{song_title} - Phase Cancelled Clean.wav",
        destination / f"{song_title} - Removed Noise.wav",
    )


def validate_output_paths(inputs: list[Path], outputs: list[Path]) -> None:
    """Check the complete write plan before opening any output."""
    input_paths: set[Path] = set()
    output_paths: set[Path] = set()
    input_files: set[tuple[int, int]] = set()
    output_files: set[tuple[int, int]] = set()
    for path in inputs:
        resolved = path.resolve()
        input_paths.add(resolved)
        identity = _file_identity(resolved)
        if identity is not None:
            input_files.add(identity)

    for path in outputs:
        resolved = path.resolve()
        identity = _file_identity(resolved)
        if resolved in input_paths or identity in input_files:
            raise InvalidInputError(f"Path collision: output would overwrite the input file ({path}).")
        if resolved in output_paths or identity in output_files:
            raise InvalidInputError(f"Path collision: multiple outputs target the same file ({path}).")
        output_paths.add(resolved)
        if identity is not None:
            output_files.add(identity)

    for path in output_paths:
        for parent in path.parents:
            if parent in output_paths:
                raise InvalidInputError(
                    f"Path collision: output is also required as an output directory ({parent})."
                )


def _file_identity(path: Path) -> tuple[int, int] | None:
    try:
        info = path.stat()
    except (FileNotFoundError, NotADirectoryError):
        return None
    # Existing hard links can resolve to distinct paths for the same file.
    return (info.st_dev, info.st_ino) if info.st_ino else None


def process_suno_wav(
    input_path: Path,
    out_dir: Path | None,
    title: str | None,
    params: ProcessingParams | None = None,
    report_path: Path | None = None,
) -> ProcessingResult:
    clean_path, noise_path = wav_output_paths(input_path, out_dir, title)
    outputs = [clean_path, noise_path]
    if report_path is not None:
        outputs.append(report_path)
    validate_output_paths([input_path], outputs)

    params = params or ProcessingParams()
    stft_config = StftConfig(
        n_fft=params.n_fft,
        hop_length=params.hop_length,
        window=params.window,
    )

    try:
        original, info = load_audio(input_path)
    except Exception as exc:  # soundfile raises LibsndfileError / RuntimeError
        raise InvalidInputError(f"Cannot read '{input_path.name}' as audio: {exc}") from exc
    _validate_audio(original, params)

    n_frames = original.shape[0]
    n_channels = original.shape[1]
    sample_rate = info.sample_rate

    spectra = []
    freqs = None
    for ch in range(n_channels):
        spec, freqs = stft_channel(original[:, ch], sample_rate, stft_config)
        spectra.append(spec)
    if freqs is None:
            raise InvalidInputError("Input audio contains no channels.")
    magnitudes = [np.abs(s) for s in spectra]
    linked_mag = linked_magnitude(magnitudes)

    noise_profile, n_quiet_frames = estimate_noise_spectrum(
        magnitudes,
        freqs,
        quiet_fraction=params.quiet_fraction,
        bass_cut_hz=params.bass_cut_hz,
    )

    gain = raw_gain_mask(
        linked_mag,
        noise_profile,
        freqs,
        oversubtraction=params.oversubtraction,
        bass_hz=params.bass_cut_hz,
    )
    gain = smooth_gain_mask(
        gain,
        freq_sigma=params.freq_smooth_sigma,
        time_sigma=params.time_smooth_sigma,
    )

    denoised = np.column_stack(
        [
            istft_channel(apply_gain_to_spectrum(spec, gain), sample_rate, stft_config, n_frames)
            for spec in spectra
        ]
    )
    denoised = align_length(denoised, n_frames)
    original = align_length(original, n_frames)
    noise_track = original - denoised

    clipped_clean = count_clipped(denoised)
    clipped_noise = count_clipped(noise_track)
    write_wav_24bit(clean_path, denoised, sample_rate)
    write_wav_24bit(noise_path, noise_track, sample_rate)

    # Verify on what is actually on disk.
    clean_rb, _ = load_wav(clean_path)
    noise_rb, _ = load_wav(noise_path)
    err = null_test_error(original, noise_rb, clean_rb)
    passed = bool(err["max_error_db"] <= params.reconstruction_threshold_db)

    peaks_clean = peak_levels(denoised)
    peaks_noise = peak_levels(noise_track)
    clip_warning = (clipped_clean + clipped_noise) > 0

    report = {
        "tool_version": __version__,
        "input": input_path.name,
        "input_sha256": sha256_file(input_path),
        "sample_rate": sample_rate,
        "channels": info.channels,
        "duration_seconds": n_frames / sample_rate,
        "processing_parameters": {
            **asdict(params),
            "max_attenuation_db": MAX_ATTENUATION_DB,
            "stereo_mode": "linked_noise_profile_shared_gain",
            "quiet_frames_used": n_quiet_frames,
        },
        "output_peaks": {
            "phase_cancelled_clean": peaks_clean,
            "removed_noise": peaks_noise,
        },
        "clipped_samples": {"phase_cancelled_clean": clipped_clean, "removed_noise": clipped_noise},
        "reconstruction": err,
        "reconstruction_passed": passed,
        "reconstruction_threshold_db": params.reconstruction_threshold_db,
        "clip_warning": clip_warning,
        "outputs": {
            "phase_cancelled_clean": clean_path.name,
            "removed_noise": noise_path.name,
        },
    }

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not passed:
        hint = " Cause: samples exceed full scale and were clipped by the 24-bit write." if clip_warning else ""
        raise RuntimeError(
            "Phase-cancel verification failed: "
            f"max_error_db={err['max_error_db']:.2f} dBFS "
            f"(threshold {params.reconstruction_threshold_db} dB).{hint} "
            "Outputs were written for inspection."
        )

    return ProcessingResult(clean_path=clean_path, noise_path=noise_path, report=report)
