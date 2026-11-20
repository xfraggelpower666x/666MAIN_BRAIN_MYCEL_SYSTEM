"""Regressionen mit echten FFmpeg-Kodierungen und isolierten Exportaufträgen."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import runpy
import subprocess
from threading import Barrier, Event, Lock
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def app():
    namespace = runpy.run_path(str(ROOT / 'MP3_Manager.pyw'), run_name='lyvra_export_test')
    return namespace['App'].convert_wavs


def make_source(path):
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                    'sine=frequency=1100:sample_rate=48000:duration=4',
                    '-ac', '2', str(path)], check=True)


def job():
    return SimpleNamespace(
        root=SimpleNamespace(after=lambda delay, func: func()),
        cancel_audio=Event(), process_lock=Lock(), active_process=None,
        audio_progress=Mock(), progress_update=Mock(), current_file=Mock(),
        wav_status=Mock(), wav_button=Mock(), file_percent=Mock(), label_file=Mock(),
        job_details=Mock(), run_interruptible=lambda cmd, event: subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8', errors='replace'),
    )


def test_concurrent_conversion_preserves_winner_and_cleans_workdirs(app, tmp_path, monkeypatch):
    source = tmp_path / 'Test (1).wav'
    make_source(source)
    original = source.read_bytes()
    output = tmp_path / 'output'
    output.mkdir()
    barrier = Barrier(2)
    publish = app.__globals__['publish_mp3_exclusive']
    monkeypatch.setattr(app.__globals__['messagebox'], 'showinfo', Mock())

    def concurrent_publish(staged, destination):
        assert not destination.exists()
        assert app.__globals__['read_tags'](staged)['TIT2'] == 'Test 1'
        barrier.wait(timeout=15)
        publish(staged, destination)

    monkeypatch.setitem(app.__globals__, 'publish_mp3_exclusive', concurrent_publish)
    workers = [job(), job()]
    settings = (48000, 320, 'fltp', 'stereo', False, -14, -2, 'maximum', True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(app, worker, [source], output, 'ffmpeg', 'ffprobe',
                               settings, {}) for worker in workers]
        for future in futures:
            future.result(timeout=25)
    assert {p.name for p in output.iterdir()} == {'Test 1.mp3', 'Test 1.mp3.quality.json'}
    states = [worker.wav_status.set.call_args.args[0] for worker in workers]
    assert sum('1 erfolgreich' in status for status in states) == 1
    assert sum('1 fehlgeschlagen' in status for status in states) == 1
    assert source.read_bytes() == original


def test_failed_qc_never_exposes_final_file(app, tmp_path, monkeypatch):
    source = tmp_path / 'quality.wav'
    make_source(source)
    output = tmp_path / 'output'
    monkeypatch.setattr(app.__globals__['messagebox'], 'showinfo', Mock())

    def reject(ffmpeg, ffprobe, staged, duration, runner):
        assert staged.parent.parent == output
        assert staged.is_file()
        assert not (output / 'quality.mp3').exists()
        raise RuntimeError('Test: Audio-QC abgelehnt')

    monkeypatch.setitem(app.__globals__, 'verify_encoded_mp3', reject)
    worker = job()
    app(worker, [source], output, 'ffmpeg', 'ffprobe',
        (48000, 320, 'fltp', 'stereo', False, -14, -2, 'maximum', True), {})
    assert list(output.iterdir()) == []
    assert '1 fehlgeschlagen' in worker.wav_status.set.call_args.args[0]


def test_balanced_uses_constant_gain_at_zero_lra(app, tmp_path, monkeypatch):
    source = tmp_path / 'linear.wav'
    make_source(source)
    monkeypatch.setattr(app.__globals__['messagebox'], 'showinfo', Mock())
    settings = (48000, 320, 'fltp', 'stereo', True, -20, -2, 'balanced', True)
    output = tmp_path / 'linear'
    worker = job()
    app(worker, [source], output, 'ffmpeg', 'ffprobe', settings, {})
    assert (output / 'linear.mp3').exists(), app.__globals__['messagebox'].showinfo.call_args
    report = json.loads((output / 'linear.mp3.quality.json').read_text())
    assert report['normalization_applied'] is True

    def integrated_loudness(path):
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-i', str(path), '-af',
             'loudnorm=I=-20:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'],
            check=True, text=True, capture_output=True,
        )
        import re
        return json.loads(re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)[-1])

    source_measurement = integrated_loudness(source)
    output_measurement = integrated_loudness(output / 'linear.mp3')
    assert float(source_measurement['input_lra']) == 0
    assert float(output_measurement['input_i']) == pytest.approx(-20, abs=0.2)

    rejected = tmp_path / 'rejected'
    app(job(), [source], rejected, 'ffmpeg', 'ffprobe',
        (48000, 320, 'fltp', 'stereo', True, -5, -16, 'balanced', True), {})
    assert list(rejected.iterdir()) == []
