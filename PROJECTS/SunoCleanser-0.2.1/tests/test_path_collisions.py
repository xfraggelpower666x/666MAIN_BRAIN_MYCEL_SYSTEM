from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from sunocleanser.cli import main
from sunocleanser.suno.pipeline import InvalidInputError, process_suno_wav


def _write_wav(path: Path, amplitude: float = 0.2) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = amplitude * np.sin(2 * np.pi * 440 * np.arange(4096) / 48000)
    sf.write(path, samples, 48000, subtype="PCM_24")
    return path.read_bytes()


def test_report_cannot_replace_input(tmp_path, capsys):
    source = tmp_path / "track.wav"
    before = _write_wav(source)
    out = tmp_path / "out"
    code = main([str(source), "--out-dir", str(out), "--report", str(source)])
    assert source.read_bytes() == before
    assert code == 5
    assert "collision" in capsys.readouterr().err.lower()
    assert not out.exists()


def test_batch_rejects_same_stem_before_writing(tmp_path, capsys):
    first = tmp_path / "a" / "shared.wav"
    second = tmp_path / "b" / "shared.wav"
    first_before = _write_wav(first)
    second_before = _write_wav(second, amplitude=0.1)
    out = tmp_path / "out"
    out.mkdir()
    previous = out / "shared.report.json"
    previous.write_text("previous result", encoding="utf-8")

    code = main([str(first), str(second), "--out-dir", str(out)])
    assert previous.read_text(encoding="utf-8") == "previous result"
    assert code == 5
    assert "collision" in capsys.readouterr().err.lower()
    assert first.read_bytes() == first_before
    assert second.read_bytes() == second_before
    assert list(out.iterdir()) == [previous]


def test_batch_cannot_replace_another_input(tmp_path, capsys):
    first = tmp_path / "track.wav"
    second = tmp_path / "track - Removed Noise.wav"
    first_before = _write_wav(first)
    second_before = _write_wav(second, amplitude=0.1)

    code = main([str(first), str(second)])
    assert second.read_bytes() == second_before
    assert code == 5
    assert "collision" in capsys.readouterr().err.lower()
    assert first.read_bytes() == first_before
    assert sorted(tmp_path.iterdir()) == sorted([first, second])


def test_report_cannot_replace_clean_wav(tmp_path):
    source = tmp_path / "track.wav"
    before = _write_wav(source)
    out = tmp_path / "out"
    report = out / "track - Phase Cancelled Clean.wav"

    with pytest.raises(InvalidInputError, match="collision"):
        process_suno_wav(source, out, None, report_path=report)
    assert source.read_bytes() == before
    assert not out.exists()


def test_report_cannot_replace_input_through_hard_link(tmp_path):
    source = tmp_path / "track.wav"
    before = _write_wav(source)
    report = tmp_path / "report.json"
    try:
        report.hardlink_to(source)
    except OSError as exc:
        pytest.skip(f"Hard links unavailable: {exc}")
    out = tmp_path / "out"

    with pytest.raises(InvalidInputError, match="collision"):
        process_suno_wav(source, out, None, report_path=report)
    assert source.read_bytes() == report.read_bytes() == before
    assert not out.exists()
