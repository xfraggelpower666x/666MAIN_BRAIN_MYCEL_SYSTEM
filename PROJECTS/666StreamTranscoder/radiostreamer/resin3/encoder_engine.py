"""Resin 3 encoder lifecycle boundary using the preserved FFmpeg MP3 command."""
import collections
import subprocess
import threading

from .. import tools
from .encoder import mp3_command


class EncoderEngine:
    def __init__(self, broadcaster):
        self.host = broadcaster
        self._threads = []

    def start(self):
        host = self.host
        command = mp3_command(host.ffmpeg, host.sr, host.ch, host.cfg["bitrate"])
        process = tools.popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        host.encoder_tail = collections.deque(maxlen=8)
        host.encoder = process
        for target in (host._encoder_out, host._encoder_err):
            worker = threading.Thread(target=target, daemon=True)
            self._threads.append(worker)
            worker.start()
        return process

    def stop(self):
        """Release encoder-owned OS pipes after terminating the encoder process."""
        process = self.host.encoder
        if process is None:
            return
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        for worker in self._threads:
            if worker.ident is not None and worker is not threading.current_thread():
                worker.join(timeout=1)
        for pipe in (process.stdin, process.stdout, process.stderr):
            if pipe is not None and not pipe.closed:
                try:
                    pipe.close()
                except OSError:
                    pass
