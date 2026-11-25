"""Lokale Medienkonvertierung mit FFmpeg, ohne Änderungen an den Eingaben."""
import json
import math
import os
from pathlib import Path
from queue import Empty, Queue
import subprocess
from tempfile import TemporaryDirectory, TemporaryFile
from threading import Thread
from time import monotonic

NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def stop_process(process):
    if process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=3)
        except ProcessLookupError:
            pass
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def inspect_media(ffprobe, source, cancel=None):
    command = [ffprobe, '-v', 'error', '-protocol_whitelist', 'file',
               '-show_streams', '-show_format', '-of', 'json', str(source)]
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Auftrag gestoppt.')
    deadline = monotonic() + 20
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding='utf-8', errors='replace', creationflags=NO_WINDOW) as process:
        try:
            while True:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError('Auftrag gestoppt.')
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise RuntimeError('Die Medienprüfung hat das Zeitlimit überschritten.')
                try:
                    stdout, stderr = process.communicate(timeout=min(.15, remaining))
                    break
                except subprocess.TimeoutExpired:
                    continue
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Auftrag gestoppt.')
            result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        finally:
            stop_process(process)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-800:] or 'FFprobe konnte die Datei nicht lesen.')
    return json.loads(result.stdout)


def positive_duration(value):
    try:
        duration = float(value)
    except (TypeError, ValueError):
        return None
    return duration if math.isfinite(duration) and duration > 0 else None


def run_ffmpeg(command, cancel, progress, duration):
    """Liest den maschinenlesbaren Fortschritt und stoppt auch ohne neue Ausgabe."""
    if cancel.is_set():
        raise InterruptedError('Auftrag gestoppt.')
    messages = Queue()
    started = monotonic()

    def read_progress(pipe):
        timestamps = {}
        for line in pipe:
            key, _, value = line.strip().partition('=')
            if key in ('out_time_us', 'out_time_ms'):
                try:
                    timestamps[key] = int(value)
                except ValueError:
                    continue
            elif key == 'progress':
                # Bei älteren Builds liefert auch out_time_ms Mikrosekunden.
                position = timestamps.get('out_time_us', timestamps.get('out_time_ms'))
                if position is not None:
                    messages.put(position / 1_000_000)
                timestamps.clear()
        messages.put(None)

    last_position = 0.0
    with TemporaryFile() as errors, subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=errors, text=True,
        encoding='utf-8', errors='replace', creationflags=NO_WINDOW,
    ) as process:
        reader = Thread(target=read_progress, args=(process.stdout,), daemon=True)
        reader.start()
        try:
            while True:
                if cancel.is_set():
                    raise InterruptedError('Auftrag gestoppt.')
                try:
                    seconds = messages.get(timeout=.15)
                except Empty:
                    continue
                if seconds is None:
                    break
                last_position = max(last_position, seconds)
                fraction = min(.99, last_position / duration) if duration else None
                progress(fraction, monotonic() - started, last_position)
            while process.poll() is None:
                if cancel.wait(.15):
                    raise InterruptedError('Auftrag gestoppt.')
            if process.returncode:
                errors.seek(0, os.SEEK_END)
                errors.seek(max(0, errors.tell() - 1600))
                raise RuntimeError(errors.read().decode('utf-8', 'replace').strip() or 'FFmpeg meldete einen Fehler.')
        finally:
            stop_process(process)
            reader.join()
    if cancel.is_set():
        raise InterruptedError('Auftrag gestoppt.')
    return last_position


def slideshow_args(images, duration, width, height, fade):
    count = len(images)
    if not 1 <= count <= 12:
        raise ValueError('Bitte 1 bis 12 Bilder auswählen.')
    if duration is None:
        raise ValueError('Für ein Covervideo muss die Audiodauer bekannt sein.')
    if (width, height) not in ((1280, 720), (1920, 1080)):
        raise ValueError('Ungültige Videogröße.')
    if count > 1 and duration / count < .2:
        raise ValueError('Audio ist für diese Bildanzahl zu kurz.')
    overlap = min(.5, duration / count / 4) if fade and count > 1 else 0
    clip = (duration + overlap * (count - 1)) / count
    inputs, filters = [], []
    for index, image in enumerate(images, 1):
        picture = Path(image).resolve(strict=True)
        inputs.extend(['-loop', '1', '-framerate', '25', '-t', f'{clip + .04:.6f}',
                       '-protocol_whitelist', 'file', '-i', str(picture)])
        filters.append(
            f'[{index}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease:force_divisible_by=2,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{index}]'
        )
    last = 'v1'
    if overlap:
        for index in range(2, count + 1):
            offset = (index - 1) * (clip - overlap)
            filters.append(f'[{last}][v{index}]xfade=duration={overlap:.6f}:offset={offset:.6f}[x{index}]')
            last = f'x{index}'
    elif count > 1:
        for index in range(1, count + 1):
            filters.append(f'[v{index}]trim=duration={clip:.6f}[t{index}]')
        sequence = ''.join(f'[t{index}]' for index in range(1, count + 1))
        filters.append(f'{sequence}concat=n={count}:v=1:a=0[slideshow]')
        last = 'slideshow'
    filters.append(f'[{last}]tpad=stop_mode=clone:stop_duration=0.25[cover]')
    return inputs, ['-filter_complex_threads', '1', '-filter_complex', ';'.join(filters), '-map', '[cover]']


def export_media(ffmpeg, ffprobe, source, stream, destination, cancel, progress,
                 publish, *, images=(), size=(1280, 720), fade=True, phase=lambda _: None):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    extension = destination.suffix.lower()
    if extension not in {'.mp3', '.wav', '.mp4'}:
        raise ValueError('Ziel muss MP3, WAV oder MP4 sein.')
    if os.path.lexists(destination):
        raise FileExistsError('Zieldatei existiert bereits. Bitte einen freien Namen wählen.')
    phase("Audiospur prüfen …")
    data = inspect_media(ffprobe, source, cancel)
    selected = next((entry for entry in data.get('streams', [])
                     if entry['index'] == stream and entry.get('codec_type') == 'audio'), None)
    if selected is None:
        raise ValueError('Die gewählte Audiospur ist nicht verfügbar.')
    stream_duration = positive_duration(selected.get('duration'))
    duration = stream_duration or positive_duration(data.get('format', {}).get('duration'))
    command = [ffmpeg, '-hide_banner', '-nostdin', '-n', '-v', 'error',
               '-progress', 'pipe:1', '-nostats', '-protocol_whitelist', 'file', '-i', str(source)]
    if extension == '.mp4':
        if stream_duration is None:
            phase('Dauer der gewählten Audiospur ermitteln …')
            scan = command + ['-map', f'0:{stream}', '-af', 'asetpts=N/SR/TB', '-f', 'null', '-']
            stream_duration = positive_duration(run_ffmpeg(scan, cancel, lambda *_: None, None))
            duration = stream_duration
        inputs, video = slideshow_args(images, duration, *size, fade)
        command += inputs + video + ['-c:v', 'libx264', '-preset', 'veryfast',
                                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-af', 'asetpts=N/SR/TB',
                                    '-shortest', '-t', f'{duration:.6f}', '-movflags', '+faststart']
        expected_audio = 'aac'
    elif extension == '.mp3':
        command += ['-vn', '-c:a', 'libmp3lame', '-b:a', '320k', '-ac', '2', '-id3v2_version', '3']
        expected_audio = 'mp3'
    else:
        command += ['-vn', '-c:a', 'pcm_s24le']
        expected_audio = 'pcm_s24le'
    command += ['-map', f'0:{stream}', '-map_metadata', '0']
    with TemporaryDirectory(prefix='.lyvra-media-', dir=destination.parent) as staging:
        candidate = Path(staging) / ('export' + extension)
        phase("Kodierung läuft …")
        run_ffmpeg(command + [str(candidate)], cancel, progress, duration)
        phase("Ausgabe vollständig prüfen …")
        output = inspect_media(ffprobe, candidate, cancel)
        codecs = [(entry['codec_type'], entry['codec_name']) for entry in output.get('streams', [])]
        expected = [('audio', expected_audio)]
        if extension == '.mp4':
            expected.append(('video', 'h264'))
        if sorted(codecs) != sorted(expected):
            raise RuntimeError('Die Ausgabedatei enthält nicht die erwarteten Streams.')
        observed = positive_duration(output.get('format', {}).get('duration'))
        if observed is None or (stream_duration and abs(observed - stream_duration) > .35):
            raise RuntimeError('Die geprüfte Ausgabedauer weicht von der Audiospur ab.')
        run_ffmpeg([ffmpeg, '-v', 'error', '-xerror', '-nostdin', '-protocol_whitelist', 'file', '-i', str(candidate),
                    '-map', '0', '-f', 'null', '-'], cancel, lambda *_: None, None)
        if cancel.is_set():
            raise InterruptedError('Auftrag gestoppt.')
        publish(candidate, destination)
