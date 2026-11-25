from pathlib import Path
import hashlib
from queue import Queue
import runpy
import subprocess
from threading import Event

from PIL import Image
import pytest

from media_tools import export_media, inspect_media


@pytest.fixture
def media(tmp_path):
    source = tmp_path / 'zwei Tonspuren.mp4'
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=s=160x90:r=25:d=2',
         '-f', 'lavfi', '-i', 'sine=frequency=440:d=2',
         '-f', 'lavfi', '-i', 'sine=frequency=880:sample_rate=48000:d=2',
         '-map', '0:v', '-map', '1:a', '-map', '2:a', '-c:v', 'libx264',
         '-c:a', 'aac', '-metadata:s:a:1', 'language=deu', str(source)], check=True)
    return source


@pytest.fixture
def publish():
    return runpy.run_path(str(Path(__file__).resolve().parents[1] / 'MP3_Manager.pyw'))['publish_mp3_exclusive']


def test_extract_selected_stream_and_preserve_input(media, publish):
    original = hashlib.sha256(media.read_bytes()).digest()
    for extension, codec in (('wav', 'pcm_s24le'), ('mp3', 'mp3')):
        destination = media.with_suffix('.' + extension)
        progress = Queue()
        export_media('ffmpeg', 'ffprobe', media, 2, destination, Event(),
                     lambda *values: progress.put(values), publish)
        [stream] = inspect_media('ffprobe', destination)['streams']
        assert (stream['codec_name'], stream['sample_rate']) == (codec, '48000')
        assert not progress.empty()
        with pytest.raises(FileExistsError):
            export_media('ffmpeg', 'ffprobe', media, 2, destination, Event(), lambda *_: None, publish)
    assert hashlib.sha256(media.read_bytes()).digest() == original
    assert not list(media.parent.glob('.lyvra-media-*'))


@pytest.mark.parametrize('fade', [False, True])
def test_covervideo_uses_both_images(media, publish, fade):
    images = []
    for color in ('red', 'blue'):
        image = media.parent / f'cover {color}.png'
        Image.new('RGB', (300, 170), color).save(image)
        images.append(image)
    destination = media.parent / 'cover output.mp4'
    export_media('ffmpeg', 'ffprobe', media, 2, destination, Event(),
                 lambda *_: None, publish, images=images, fade=fade)
    video, = [s for s in inspect_media('ffprobe', destination)['streams'] if s['codec_type'] == 'video']
    assert (video['width'], video['height']) == (1280, 720)
    for position, channel in (('.2', 0), ('1.8', 2)):
        pixel = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss',
                    '0.2' if position == '.2' else position, '-i', str(destination),
                    '-frames:v', '1', '-vf', 'scale=1:1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
        assert pixel[channel] > 180


def test_cancel_running_process_removes_output(media, publish):
    target = media.with_suffix('.wav')
    cancel = Event()
    with pytest.raises(InterruptedError):
        export_media('ffmpeg', 'ffprobe', media, 2, target, cancel,
                     lambda *_: cancel.set(), publish)
    assert not target.exists()
    assert not list(media.parent.glob('.lyvra-media-*'))


def test_covervideo_uses_shorter_mkv_audio_instead_of_container_duration(tmp_path, publish):
    source = tmp_path / 'long video short sound.mkv'
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=s=160x90:r=25:d=8',
         '-f', 'lavfi', '-i', 'sine=frequency=880:sample_rate=48000:d=2.03',
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-c:a', 'pcm_s16le', str(source)], check=True,
    )
    streams = inspect_media('ffprobe', source)
    audio = next(s for s in streams['streams'] if s['codec_type'] == 'audio')
    assert 'duration' not in audio
    assert float(streams['format']['duration']) >= 8
    covers = []
    for color in ('red', 'blue'):
        picture = tmp_path / f'{color}.png'
        Image.new('RGB', (320, 180), color).save(picture)
        covers.append(picture)
    target = tmp_path / 'result.mp4'
    export_media('ffmpeg', 'ffprobe', source, audio['index'], target, Event(),
                 lambda *_: None, publish, images=covers)
    output = inspect_media('ffprobe', target)
    assert float(output['format']['duration']) == pytest.approx(2.03, abs=.10)
    pixel = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '1.8', '-i', str(target),
                                      '-frames:v', '1', '-vf', 'scale=1:1', '-pix_fmt', 'rgb24',
                                      '-f', 'rawvideo', '-'])
    assert pixel[2] > 180


def test_legacy_progress_is_in_microseconds_and_can_be_stopped(tmp_path):
    import sys
    from media_tools import run_ffmpeg

    reported = []
    cancel = Event()
    command = [sys.executable, '-u', '-c',
               "print('out_time_ms=1250000\\nprogress=continue'); import time; time.sleep(30)"]

    def stop_after_first_update(fraction, elapsed, seconds):
        reported.append((fraction, seconds))
        cancel.set()

    with pytest.raises(InterruptedError):
        run_ffmpeg(command, cancel, stop_after_first_update, 2.5)
    assert reported == [(0.5, 1.25)]


def test_destination_symlink_is_a_collision(media, publish):
    target = media.with_suffix('.wav')
    referenced_file = media.parent / 'not-created.wav'
    try:
        target.symlink_to(referenced_file)
    except OSError:
        pytest.skip('This host does not allow creating symlinks')
    with pytest.raises(FileExistsError):
        export_media('ffmpeg', 'ffprobe', media, 2, target, Event(), lambda *_: None, publish)
    assert target.is_symlink()
    assert not referenced_file.exists()
