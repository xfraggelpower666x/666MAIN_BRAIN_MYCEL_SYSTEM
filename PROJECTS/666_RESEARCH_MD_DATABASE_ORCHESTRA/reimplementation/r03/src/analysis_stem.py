"""Per-stem streaming PCM decoding and bounded FFT measurements."""
from __future__ import annotations
import hashlib
import math
import wave
from typing import Any
from .numpy_compat import np
from .constants import (BANDS, FFT_SIZE, MAX_CHANNELS, MAX_WORKING_MEMORY_BYTES, _dbfs, _fail)
from .wav_io import _decode_pcm

def _stereo_correlation(sums: dict[str, float], count: int) -> float | None:
    if count <= 0:
        return None
    cov = sums["lr"] - sums["l"] * sums["r"] / count
    var_l = sums["ll"] - sums["l"] * sums["l"] / count
    var_r = sums["rr"] - sums["r"] * sums["r"] / count
    denom = math.sqrt(max(0.0, var_l) * max(0.0, var_r))
    if denom <= 1e-20:
        return None
    return max(-1.0, min(1.0, cov / denom))

def _analyze_one(item: dict[str, Any], common_frames: int) -> dict[str, Any]:
    channels = item["channels"]
    width = item["sample_width_bytes"]
    rate = item["sample_rate"]
    total_samples = 0
    sum_squares = 0.0
    peak = 0.0
    clipped = 0
    frame_rms: list[float] = []
    band_weighted: dict[str, float] = {name: 0.0 for name, _, _ in BANDS}
    total_weighted = 0.0
    weight_sum = 0.0
    stereo_sums = {"l": 0.0, "r": 0.0, "ll": 0.0, "rr": 0.0, "lr": 0.0}
    stereo_frames = 0
    analysis_windows = 0
    source_hash = hashlib.sha256()
    frames_left = common_frames
    fft_memory_estimate = FFT_SIZE * channels * 8 * 5 + FFT_SIZE * 16 * 3
    if fft_memory_estimate > MAX_WORKING_MEMORY_BYTES:
        _fail("FFT_WORKING_MEMORY_GUARD")

    try:
        with wave.open(str(item["path"]), "rb") as reader:
            freqs = np.fft.rfftfreq(FFT_SIZE, d=1.0 / rate)
            while frames_left > 0:
                frame_count = min(FFT_SIZE, frames_left)
                raw = reader.readframes(frame_count)
                expected = frame_count * channels * width
                if len(raw) != expected:
                    _fail("TRUNCATED_WAV_DATA:" + item["role"])
                source_hash.update(raw)
                samples = _decode_pcm(raw, width, channels)
                frames_left -= frame_count
                total_samples += samples.size
                sum_squares += float(np.sum(samples * samples, dtype=np.float64))
                peak = max(peak, float(np.max(np.abs(samples))))
                scale = float(1 << (width * 8 - 1))
                clip_threshold = 1.0 - 1.0 / scale
                clipped += int(np.count_nonzero(np.abs(samples) >= clip_threshold))
                frame_rms.append(float(np.sqrt(np.mean(samples * samples))))

                if channels == 2:
                    left = samples[:, 0]
                    right = samples[:, 1]
                    stereo_sums["l"] += float(np.sum(left))
                    stereo_sums["r"] += float(np.sum(right))
                    stereo_sums["ll"] += float(np.dot(left, left))
                    stereo_sums["rr"] += float(np.dot(right, right))
                    stereo_sums["lr"] += float(np.dot(left, right))
                    stereo_frames += frame_count

                # Per-window Hann weighting limits leakage; the final short block is zero-padded.
                if frame_count >= 8:
                    window = np.hanning(frame_count)
                else:
                    window = np.ones(frame_count, dtype=np.float64)
                window_power = float(np.sum(window * window))
                windowed = samples * window[:, None]
                spectrum = np.fft.rfft(windowed, n=FFT_SIZE, axis=0)
                power = np.mean(np.abs(spectrum) ** 2, axis=1)
                one_sided = power.copy()
                if one_sided.size > 2:
                    one_sided[1:-1] *= 2.0
                denom = FFT_SIZE * window_power
                if denom <= 0.0:
                    _fail("INVALID_WINDOW_NORMALIZATION")
                total_weighted += float(np.sum(one_sided)) / denom * window_power
                for name, low, high in BANDS:
                    effective_high = min(high, rate / 2.0)
                    if effective_high <= low:
                        continue
                    mask = (freqs >= low) & (freqs < effective_high)
                    if np.any(mask):
                        band_ms = float(np.sum(one_sided[mask])) / denom
                        band_weighted[name] += band_ms * window_power
                weight_sum += window_power
                analysis_windows += 1
    except (wave.Error, EOFError, OSError) as exc:
        raise AnalysisError("WAV_READ_FAILED:" + item["role"]) from exc

    if total_samples == 0 or weight_sum <= 0.0:
        _fail("NO_ANALYZABLE_AUDIO:" + item["role"])
    mean_square = sum_squares / total_samples
    rms = math.sqrt(mean_square)
    rms_db = _dbfs(mean_square)
    peak_db = _dbfs(peak * peak)
    band_power = {name: value / weight_sum for name, value in band_weighted.items()}
    mapped_total = sum(band_power.values())
    shares = {name: (value / mapped_total if mapped_total > 0.0 else 0.0) for name, value in band_power.items()}
    band_report: dict[str, Any] = {}
    nyquist = rate / 2.0
    for name, low, high in BANDS:
        effective_high = min(high, nyquist)
        band_report[name] = {
            "low_hz": low,
            "high_hz": high,
            "effective_high_hz": effective_high,
            "available": effective_high > low,
            "partial_band": effective_high < high and effective_high > low,
            "energy_dbfs": _dbfs(band_power[name]),
            "share_percent": round(shares[name] * 100.0, 4),
        }
    unmapped = max(0.0, total_weighted / weight_sum - mapped_total)
    sorted_rms = sorted(frame_rms)
    median_rms = float(np.median(sorted_rms))
    p95_rms = float(np.percentile(sorted_rms, 95))
    transient_ratio = p95_rms / median_rms if median_rms > 1e-12 else (0.0 if p95_rms <= 1e-12 else None)
    corr = _stereo_correlation(stereo_sums, stereo_frames) if channels == 2 else None
    duration = item["duration_seconds"]
    return {
        "role": item["role"],
        "source_file": item["relative_path"],
        "source_sha256_analyzed_audio_bytes": source_hash.hexdigest(),
        "file_bytes": item["file_bytes"],
        "analysis_windows": analysis_windows,
        "sample_rate_hz": rate,
        "channels": channels,
        "pcm_bits": item["sample_width_bits"],
        "source_duration_seconds": round(duration, 6),
        "analyzed_duration_seconds": round(common_frames / rate, 6),
        "excluded_tail_seconds": round(max(0.0, duration - common_frames / rate), 6),
        "rms_dbfs": round(rms_db, 4),
        "peak_dbfs": round(peak_db, 4),
        "crest_factor_db": round(peak_db - rms_db, 4),
        "clipped_sample_count": clipped,
        "clipped_sample_percent": round(clipped / total_samples * 100.0, 6),
        "stereo_correlation": round(corr, 6) if corr is not None else None,
        "mono_compatibility": "WATCH_NEGATIVE_CORRELATION" if corr is not None and corr < -0.25 else ("CHECK" if corr is not None and corr < 0.0 else "OK_OR_NOT_STEREO"),
        "transient_p95_to_median_rms_ratio": round(transient_ratio, 5) if transient_ratio is not None else None,
        "mapped_band_energy_percent": round(mapped_total / max(total_weighted / weight_sum, 1e-20) * 100.0, 4),
        "unmapped_energy_percent": round(unmapped / max(total_weighted / weight_sum, 1e-20) * 100.0, 4),
        "bands": band_report,
    }
