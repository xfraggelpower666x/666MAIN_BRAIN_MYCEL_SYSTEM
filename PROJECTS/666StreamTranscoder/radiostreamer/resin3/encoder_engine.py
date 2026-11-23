"""Resin 3 encoder lifecycle boundary using the preserved FFmpeg MP3 command."""
import collections
import subprocess
import threading

from .. import tools
from .encoder import mp3_command


class EncoderEngine:
    def __init__(self, broadcaster):
        self.host = broadcaster

    def start(self):
        host = self.host
        command = mp3_command(host.ffmpeg, host.sr, host.ch, host.cfg["bitrate"])
        process = tools.popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        host.encoder_tail = collections.deque(maxlen=8)
        host.encoder = process
        threading.Thread(target=host._encoder_out, daemon=True).start()
        threading.Thread(target=host._encoder_err, daemon=True).start()
        return process
