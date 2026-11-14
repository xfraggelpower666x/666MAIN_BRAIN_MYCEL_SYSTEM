from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from sunocleanser.cli import main as cli_main
from sunocleanser.suno.pipeline import (
    InvalidInputError,
    ProcessingParams,
    process_suno_wav,
)

SR = 44100


def _tone(seconds: float = 2.0) -> np.ndarray:
    t = np.linspace(0, seconds, int(SR * seconds), endpoint=False)
    return 0.4 * np.sin(2 * np.pi * 440 * t)


def _write(path: Path, audio: np.ndarray, sr: int = SR, subtype: str = "PCM_24") -> Path:
    sf.write(path, audio, sr, subtype=subtype)
    return path


def _noisy_stereo() -> np.ndarray:
    tone = _tone()
    noise = 0.05 * np.random.default_rng(0).standard_normal(tone.shape)
    return np.column_stack([tone + noise, tone * 0.9 + noise])


def test_phase_cancel_matches_readback(tmp_path: Path) -> None:
    src = _write(tmp_path / "in.wav", _noisy_stereo())
    result = process_suno_wav(src, tmp_path, "Test", report_path=tmp_path / "r.json")

    assert result.clean_path.is_file() and result.noise_path.is_file()
    rep = result.report
    assert rep["reconstruction_passed"] is True
    # 24-bit quantisation floor is about -138 dBFS; the check must see real, tiny error.
    assert -200 < rep["reconstruction"]["max_error_db"] < -100
    assert rep["input_sha256"] and rep["tool_version"]
    assert json.loads((tmp_path / "r.json").read_text())["input"] == "in.wav"


def test_verification_detects_corrupted_noise_file(tmp_path: Path, monkeypatch) -> None:
    """The check must fail if the written files do not null (it is not tautological)."""
    import sunocleanser.suno.pipeline as pl

    real_write = pl.write_wav_24bit

    def bad_write(path, audio, sr):
        if "Removed Noise" in path.name:
            audio = audio * 0.5
        real_write(path, audio, sr)

    monkeypatch.setattr(pl, "write_wav_24bit", bad_write)
    src = _write(tmp_path / "in.wav", _noisy_stereo())
    with pytest.raises(RuntimeError, match="verification failed"):
        process_suno_wav(src, tmp_path, "Bad")


def test_mono_stays_mono(tmp_path: Path) -> None:
    src = _write(tmp_path / "m.wav", _tone() + 0.02 * np.random.default_rng(1).standard_normal(2 * SR))
    res = process_suno_wav(src, tmp_path, "Mono")
    assert sf.info(res.clean_path).channels == 1
    assert res.report["reconstruction_passed"] is True


def test_multichannel_is_preserved(tmp_path: Path) -> None:
    rng = np.random.default_rng(2)
    audio = np.column_stack([_tone() * g + 0.02 * rng.standard_normal(2 * SR) for g in (1, 0.8, 0.6, 0.5, 0.4, 0.3)])
    src = _write(tmp_path / "six.wav", audio)
    res = process_suno_wav(src, tmp_path, "Six")
    assert sf.info(res.clean_path).channels == 6
    assert len(res.report["output_peaks"]["phase_cancelled_clean"]["per_channel"]) == 6
    assert res.report["reconstruction_passed"] is True


def test_silence_does_not_crash(tmp_path: Path) -> None:
    src = _write(tmp_path / "s.wav", np.zeros((SR, 2)))
    assert process_suno_wav(src, tmp_path, "Silence").report["reconstruction_passed"] is True


def test_different_sample_rate(tmp_path: Path) -> None:
    src = _write(tmp_path / "k.wav", np.column_stack([_tone()] * 2), sr=48000)
    assert process_suno_wav(src, tmp_path, "K48").report["sample_rate"] == 48000


def test_too_short_file_gives_clear_error(tmp_path: Path) -> None:
    src = _write(tmp_path / "short.wav", 0.1 * np.random.default_rng(3).standard_normal((500, 2)))
    with pytest.raises(InvalidInputError, match="too short"):
        process_suno_wav(src, tmp_path, "Short")


def test_not_audio_gives_clear_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"this is not a wav file")
    with pytest.raises(InvalidInputError, match="Cannot read"):
        process_suno_wav(bad, tmp_path, "Bad")


def test_never_overwrites_input(tmp_path: Path) -> None:
    src = _write(tmp_path / "X - Removed Noise.wav", _noisy_stereo())
    before = src.read_bytes()
    with pytest.raises(InvalidInputError, match="overwrite"):
        process_suno_wav(src, tmp_path, "X")
    assert src.read_bytes() == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_fft": 16},
        {"hop_length": 0},
        {"hop_length": 4096},
        {"quiet_fraction": 0.0},
        {"quiet_fraction": 1.5},
        {"window": "nonsense"},
        {"oversubtraction": -1.0},
    ],
)
def test_invalid_params_rejected(kwargs) -> None:
    with pytest.raises(InvalidInputError):
        ProcessingParams(**kwargs)


def test_clipping_is_reported(tmp_path: Path) -> None:
    loud = np.clip(_noisy_stereo() * 8, -1.0, 1.0)
    src = _write(tmp_path / "loud.wav", loud)
    try:
        res = process_suno_wav(src, tmp_path, "Loud")
        assert "clipped_samples" in res.report
    except RuntimeError as exc:  # overshoot clipped on write -> verification flags it
        assert "clipped" in str(exc) or "verification failed" in str(exc)


def test_cli_exit_codes(tmp_path: Path, capsys) -> None:
    good = _write(tmp_path / "g.wav", _noisy_stereo())
    assert cli_main([str(good), "--out-dir", str(tmp_path / "o")]) == 0
    assert (tmp_path / "o" / "g.report.json").is_file()
    assert cli_main([str(tmp_path / "missing.wav")]) == 1
    short = _write(tmp_path / "s.wav", np.zeros((100, 2)))
    assert cli_main([str(short)]) == 5
    assert cli_main([str(good), "--hop", "0"]) == 5


def test_cli_batch(tmp_path: Path) -> None:
    a = _write(tmp_path / "a.wav", _noisy_stereo())
    b = _write(tmp_path / "b.wav", _noisy_stereo())
    out = tmp_path / "out"
    assert cli_main([str(a), str(b), "--out-dir", str(out), "--quiet"]) == 0
    assert (out / "a - Phase Cancelled Clean.wav").is_file()
    assert (out / "b - Removed Noise.wav").is_file()
    # one bad file must not stop the others, and the exit code must signal the failure
    bad = _write(tmp_path / "bad.wav", np.zeros((10, 2)))
    assert cli_main([str(bad), str(a), "--out-dir", str(out), "--quiet"]) == 5
    assert cli_main([str(a), str(b), "--title", "X"]) == 5
