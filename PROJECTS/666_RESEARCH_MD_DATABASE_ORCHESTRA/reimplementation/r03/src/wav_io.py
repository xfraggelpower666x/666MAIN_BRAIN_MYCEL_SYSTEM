"""Bounded WAV input validation, PCM decoding and safe report writing."""
from __future__ import annotations
import json
import os
import tempfile
import wave
from pathlib import Path, PurePosixPath
from typing import Any, Sequence
from .numpy_compat import np
from .constants import (ALLOWED_ROLES, MAX_STEMS, MIN_STEMS, MAX_TOTAL_INPUT_BYTES,
    MAX_CHANNELS, MIN_SAMPLE_RATE, MAX_SAMPLE_RATE, MAX_DURATION_SECONDS, AnalysisError, _fail)

def _resolve_inputs(input_dir: str | Path, specs: Sequence[tuple[str, str]]) -> tuple[Path, list[dict[str, Any]]]:
    root = Path(input_dir).expanduser().resolve(strict=True)
    if not root.is_dir():
        _fail("INPUT_PATH_NOT_DIRECTORY")
    if not MIN_STEMS <= len(specs) <= MAX_STEMS:
        _fail("INVALID_STEM_COUNT")
    roles = [role for role, _ in specs]
    if any(role not in ALLOWED_ROLES for role in roles):
        _fail("UNKNOWN_STEM_ROLE")
    if len(set(roles)) != len(roles):
        _fail("DUPLICATE_STEM_ROLE")

    result: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    total_bytes = 0
    for role, filename in specs:
        if not isinstance(filename, str) or not filename or "\\" in filename or ":" in filename:
            _fail("INVALID_RELATIVE_STEM_PATH")
        rel = PurePosixPath(filename)
        if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
            _fail("PATH_TRAVERSAL_BLOCKED")
        candidate = (root / Path(*rel.parts)).resolve(strict=True)
        try:
            candidate.relative_to(root)
        except ValueError:
            _fail("STEM_PATH_ESCAPES_INPUT_ROOT")
        if not candidate.is_file():
            _fail("STEM_NOT_A_FILE:" + role)
        if candidate in seen_paths:
            _fail("DUPLICATE_STEM_FILE")
        seen_paths.add(candidate)
        if candidate.suffix.lower() != ".wav":
            _fail("UNSUPPORTED_AUDIO_CONTAINER:" + role)
        size = candidate.stat().st_size
        total_bytes += size
        result.append({"role": role, "path": candidate, "relative_path": rel.as_posix(), "file_bytes": size})
    if total_bytes > MAX_TOTAL_INPUT_BYTES:
        _fail("TOTAL_INPUT_BYTES_LIMIT_EXCEEDED")
    return root, result

def _inspect_wave(item: dict[str, Any]) -> dict[str, Any]:
    path: Path = item["path"]
    try:
        with wave.open(str(path), "rb") as reader:
            channels = reader.getnchannels()
            sample_width = reader.getsampwidth()
            sample_rate = reader.getframerate()
            frames = reader.getnframes()
            compression = reader.getcomptype()
    except (wave.Error, EOFError, OSError) as exc:
        raise AnalysisError("INVALID_OR_UNREADABLE_WAV:" + item["role"]) from exc

    if compression != "NONE":
        _fail("COMPRESSED_WAV_NOT_SUPPORTED:" + item["role"])
    if channels < 1 or channels > MAX_CHANNELS:
        _fail("UNSUPPORTED_CHANNEL_COUNT:" + item["role"])
    if sample_width not in (1, 2, 3, 4):
        _fail("UNSUPPORTED_PCM_WIDTH:" + item["role"])
    if sample_rate < MIN_SAMPLE_RATE or sample_rate > MAX_SAMPLE_RATE:
        _fail("SAMPLE_RATE_OUT_OF_RANGE:" + item["role"])
    if frames <= 0:
        _fail("EMPTY_AUDIO:" + item["role"])
    duration = frames / sample_rate
    if duration > MAX_DURATION_SECONDS:
        _fail("DURATION_LIMIT_EXCEEDED:" + item["role"])
    return {
        **item,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "sample_width_bits": sample_width * 8,
        "sample_rate": sample_rate,
        "frames": frames,
        "duration_seconds": duration,
    }

def _decode_pcm(raw: bytes, sample_width: int, channels: int) -> np.ndarray:
    """Decode one bounded PCM block to normalized float64 [frames, channels]."""
    if sample_width == 1:
        values = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sample_width == 2:
        values = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    elif sample_width == 3:
        packed = np.frombuffer(raw, dtype=np.uint8)
        if packed.size % 3:
            _fail("MISALIGNED_24BIT_PCM")
        triples = packed.reshape(-1, 3).astype(np.int32)
        unsigned = triples[:, 0] | (triples[:, 1] << 8) | (triples[:, 2] << 16)
        signed = (unsigned ^ 0x800000) - 0x800000
        values = signed.astype(np.float64) / 8388608.0
    elif sample_width == 4:
        values = np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2147483648.0
    else:  # guarded by _inspect_wave; keep the decoder fail-closed independently
        _fail("UNSUPPORTED_PCM_WIDTH")
    if values.size % channels:
        _fail("MISALIGNED_PCM_CHANNEL_DATA")
    return values.reshape(-1, channels)

def write_report(report: dict[str, Any], output_dir: str | Path, input_dir: str | Path, force: bool = False) -> Path:
    """Write only to an explicitly selected output folder, atomically and without silent overwrite."""
    root = Path(input_dir).expanduser().resolve(strict=True)
    target_dir = Path(output_dir).expanduser().resolve(strict=False)
    try:
        target_dir.relative_to(root)
    except ValueError:
        pass
    else:
        _fail("OUTPUT_DIRECTORY_MUST_NOT_BE_INSIDE_INPUT")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "stem-analysis-r03.json"
    if target.exists() and not force:
        _fail("OUTPUT_EXISTS_USE_FORCE")
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".stem-analysis-r03-", suffix=".tmp", dir=str(target_dir))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return target
