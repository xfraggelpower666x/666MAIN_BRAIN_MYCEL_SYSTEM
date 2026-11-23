"""Pairwise spectral overlap and whole-session orchestration."""
from __future__ import annotations
from typing import Any, Sequence
from .constants import (SCHEMA, ALLOWED_ROLES, BANDS, FFT_SIZE, MAX_CHANNELS, MAX_SAMPLE_RATE, MAX_STEMS,
    MAX_TOTAL_INPUT_BYTES, MAX_WORKING_MEMORY_BYTES, DURATION_TOLERANCE_SECONDS,
    MAX_DURATION_SECONDS, DB_FLOOR, _fail)
from .wav_io import _resolve_inputs, _inspect_wave
from .analysis_stem import _analyze_one

def _pairwise(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_bands = a["bands"]
    b_bands = b["bands"]
    overlap = 0.0
    per_band: dict[str, Any] = {}
    for name, _, _ in BANDS:
        sa = a_bands[name]["share_percent"] / 100.0
        sb = b_bands[name]["share_percent"] / 100.0
        shared = min(sa, sb)
        overlap += shared
        ea = a_bands[name]["energy_dbfs"]
        eb = b_bands[name]["energy_dbfs"]
        gap = abs(ea - eb)
        band_overlap = min(1.0, 2.0 * shared)
        band_pressure = 0.0 if ea <= DB_FLOOR and eb <= DB_FLOOR else band_overlap * (0.5 + 0.5 * min(gap / 24.0, 1.0))
        per_band[name] = {
            "shared_spectral_share_percent": round(shared * 100.0, 4),
            "overlap_percent": round(band_overlap * 100.0, 4),
            "level_gap_db": round(gap, 4),
            "heuristic_pressure_percent": round(band_pressure * 100.0, 4),
        }
    level_gap = abs(a["rms_dbfs"] - b["rms_dbfs"])
    level_pressure = 0.5 + 0.5 * min(level_gap / 24.0, 1.0)
    pressure = 0.0 if overlap <= 0.0 else overlap * level_pressure
    if abs(a["rms_dbfs"] - b["rms_dbfs"]) < 1.0:
        dominant = "balanced"
        masked = None
    elif a["rms_dbfs"] > b["rms_dbfs"]:
        dominant, masked = a["role"], b["role"]
    else:
        dominant, masked = b["role"], a["role"]
    return {
        "roles": [a["role"], b["role"]],
        "spectral_overlap_percent": round(overlap * 100.0, 4),
        "overall_level_gap_db": round(level_gap, 4),
        "dominant_role": dominant,
        "potentially_masked_role": masked,
        "heuristic_masking_pressure_percent": round(pressure * 100.0, 4),
        "bands": per_band,
    }

def analyze_stems(input_dir: str | Path, specs: Sequence[tuple[str, str]]) -> dict[str, Any]:
    """Analyze aligned WAV stems without loading any full source file into memory."""
    _, raw_items = _resolve_inputs(input_dir, specs)
    inspected = [_inspect_wave(item) for item in raw_items]
    rates = {item["sample_rate"] for item in inspected}
    if len(rates) != 1:
        _fail("SAMPLE_RATE_MISMATCH")
    rate = next(iter(rates))
    durations = [item["duration_seconds"] for item in inspected]
    if max(durations) - min(durations) > DURATION_TOLERANCE_SECONDS + 1e-9:
        _fail("DURATION_MISMATCH_EXCEEDS_TOLERANCE")
    common_frames = min(item["frames"] for item in inspected)
    common_duration = common_frames / rate
    stems = [_analyze_one(item, common_frames) for item in inspected]
    pairs = [_pairwise(stems[i], stems[j]) for i in range(len(stems)) for j in range(i + 1, len(stems))]
    return {
        "schema": SCHEMA,
        "status": "ANALYSIS_COMPLETE_HEURISTIC_MASKING_ONLY",
        "method": {
            "spectral_engine": "NumPy real FFT (rFFT)",
            "window": "Hann",
            "fft_size_frames": FFT_SIZE,
            "hop_size_frames": FFT_SIZE,
            "analysis_mode": "bounded streaming, one stem at a time",
            "masking_index": "spectral-share overlap multiplied by relative level pressure",
            "masking_index_is_not": "not a validated psychoacoustic masking threshold, critical-band or simultaneous-masking model; not LUFS",
            "level_unit": "dBFS, not LUFS",
            "frequency_bands_hz": [{"id": name, "low": low, "high": high} for name, low, high in BANDS],
        },
        "input": {
            "sample_rate_hz": rate,
            "comparison_duration_seconds": round(common_duration, 6),
            "duration_tolerance_seconds": DURATION_TOLERANCE_SECONDS,
            "max_duration_seconds": MAX_DURATION_SECONDS,
            "roles_present": [item["role"] for item in inspected],
            "roles_missing": [role for role in ALLOWED_ROLES if role not in {item["role"] for item in inspected}],
            "total_input_bytes": sum(item["file_bytes"] for item in inspected),
            "duration_alignment": "explicit_common_overlap; excluded tails reported per stem",
        },
        "resource_limits": {
            "max_stems": MAX_STEMS,
            "max_sample_rate_hz": MAX_SAMPLE_RATE,
            "max_channels": MAX_CHANNELS,
            "max_total_input_bytes": MAX_TOTAL_INPUT_BYTES,
            "max_working_memory_bytes": MAX_WORKING_MEMORY_BYTES,
            "estimated_fft_window_memory_bytes": FFT_SIZE * MAX_CHANNELS * 8 * 5 + FFT_SIZE * 16 * 3,
            "source_files_loaded_whole": False,
        },
        "stems": stems,
        "pairwise": pairs,
        "limitations": [
            "Only uncompressed integer PCM WAV is accepted; convert other formats separately.",
            "Masking pressure is an explainable spectral-overlap heuristic, not a validated psychoacoustic masking threshold.",
            "No LUFS/BS.1770 loudness claim is made; levels are sample-based dBFS.",
            "Synthetic fixtures validate code behavior only; a real user-stem report requires real aligned stems.",
        ],
    }
