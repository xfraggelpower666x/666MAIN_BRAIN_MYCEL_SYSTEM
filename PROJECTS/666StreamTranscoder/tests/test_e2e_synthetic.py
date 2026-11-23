"""R08 isolated FFmpeg + PCM + HTTP listener end-to-end tests. No external radio service."""
import math
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import unittest
import urllib.request
import wave
from pathlib import Path
from unittest.mock import patch

from radiostreamer import config
from radiostreamer.engine import Broadcaster, Playlist
from radiostreamer.localserver import LocalServer as RealLocalServer


def make_tone(path, hz, duration=7):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        frames = b"".join(
            struct.pack("<hh", value, value)
            for value in (
                int(9500 * math.sin(2 * math.pi * hz * i / 44100))
                for i in range(44100)
            )
        )
        wav.writeframes(frames * duration)


def available_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def mp3_is_audible(encoded):
    decoder = subprocess.run(
        [shutil.which("ffmpeg"), "-hide_banner", "-nostdin", "-loglevel", "error",
         "-f", "mp3", "-i", "pipe:0", "-ar", "44100", "-ac", "1", "-f", "s16le", "pipe:1"],
        input=encoded, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=10, check=False
    )
    if decoder.returncode or len(decoder.stdout) < 4096:
        return False
    samples = (int.from_bytes(decoder.stdout[i:i + 2], "little", signed=True)
               for i in range(0, len(decoder.stdout) - 1, 2))
    return max(abs(sample) for sample in samples) > 1500


@unittest.skipUnless(shutil.which("ffmpeg"), "Real FFmpeg required")
class IsolatedBroadcastE2ETests(unittest.TestCase):
    """An HTTP listener and a persistent encoder survive both track transitions."""

    def run_pipeline(self, request_skip=False):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / "tone_a.wav", Path(tmp) / "tone_b.wav"]
            make_tone(paths[0], 220)
            make_tone(paths[1], 440)
            port = available_port()
            cfg = dict(config.DEFAULTS, source="queue", server_type=config.BUILTIN,
                       host_mode="lan", local_port=port, name="R08 Local E2E",
                       title_source="Manual", loop=False, normalize=False,
                       crossfade=True, crossfade_seconds=3)
            items = [{"kind": "file", "src": str(path), "title": path.stem} for path in paths]
            events = []
            broadcaster = Broadcaster(cfg, Playlist(items, loop=False),
                                      lambda kind, payload=None: events.append((kind, payload)))
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            # Force loopback-only binding. No tunnel, public server, or external credentials.
            with patch("radiostreamer.engine.upnp.local_ip", return_value="127.0.0.1"), \
                 patch("radiostreamer.engine.LocalServer",
                       side_effect=lambda port, _bind, **kw: RealLocalServer(port, "127.0.0.1", **kw)):
                broadcaster.start()
            try:
                response = opener.open(f"http://127.0.0.1:{port}/stream.mp3", timeout=6)
                with response:
                    original_encoder = broadcaster.encoder
                    mp3_bytes = bytearray()
                    skip_sent = False
                    next_track_at = None
                    deadline = time.monotonic() + 17
                    while time.monotonic() < deadline:
                        packet = response.read(2048)
                        if not packet:
                            break
                        mp3_bytes.extend(packet)
                        tracks = [p for kind, p in events if kind == "track" and p]
                        if request_skip and not skip_sent and tracks and len(mp3_bytes) > 20000:
                            broadcaster.skip()
                            skip_sent = True
                        if len(tracks) >= 2 and next_track_at is None:
                            next_track_at = time.monotonic()
                        if next_track_at is not None and time.monotonic() - next_track_at > 3.4:
                            break
                    self.assertIs(original_encoder, broadcaster.encoder,
                                  "Encoder restarted during transition")
                    self.assertIsNone(original_encoder.poll(), "Encoder unexpectedly exited")
                    self.assertGreater(len(mp3_bytes), 30000, "HTTP received too few MP3 bytes")
                    self.assertIsNotNone(next_track_at, "Second track never started")
                    self.assertTrue(any("Crossfade:" in str(p) for kind, p in events
                                        if kind == "log"), "Crossfade transition not observed")
                    self.assertFalse([p for kind, p in events if kind == "fatal"])
                    self.assertTrue(mp3_is_audible(bytes(mp3_bytes)),
                                    "Encoded HTTP output is not audible decoded PCM")
                    if request_skip:
                        self.assertTrue(skip_sent, "Skip command was never sent")
            finally:
                broadcaster.stop()

    def test_automatic_crossfade_preserves_encoder_and_listener(self):
        self.run_pipeline(request_skip=False)

    def test_skip_crossfade_preserves_encoder_and_listener(self):
        self.run_pipeline(request_skip=True)


if __name__ == "__main__":
    unittest.main()
