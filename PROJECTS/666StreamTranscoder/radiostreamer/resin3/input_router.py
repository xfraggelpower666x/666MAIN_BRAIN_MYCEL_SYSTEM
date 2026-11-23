"""Resin 3 input boundary delegating decoding and capture to preserved 3DX primitives."""
import sys

from .. import tools
from ..protocol import StreamError
from .source_audio import create_capture
from .source_stream import display_name, stream_input_args


class InputRouter:
    def __init__(self, broadcaster):
        self.host = broadcaster

    def open_live(self):
        # Import at runtime to avoid a module cycle: Broadcaster owns the shared PCMSource type.
        from ..engine import PCMSource
        host = self.host
        source = host.cfg["source"]
        if source in ("loopback", "app"):
            capture = create_capture(source, host.cfg)
            cmd = [host.ffmpeg, "-hide_banner", "-nostdin", "-nostats", "-loglevel", "error",
                   "-probesize", "32", "-analyzeduration", "0", "-fflags", "nobuffer",
                   "-f", "s16le", "-ar", str(capture.rate), "-ac", str(capture.channels), "-i", "pipe:0",
                   "-f", "s16le", "-ar", str(host.sr), "-ac", str(host.ch), "pipe:1"]
            src = PCMSource(cmd, host.chunk_bytes, True, title=capture.name, feeder=capture)
        elif source == "relay":
            url = str(host.cfg.get("relay_url", "")).strip()
            if not url:
                raise StreamError("Enter an HTTP(S) radio stream URL.")
            try:
                args = stream_input_args(url)
            except ValueError as exc:
                raise StreamError(str(exc)) from exc
            src = PCMSource(host._decoder_cmd(args, True), host.chunk_bytes, True,
                            title=display_name(url))
        else:
            device = host.cfg.get("device", "")
            if not device and sys.platform == "win32":
                raise StreamError("No input device selected.")
            src = PCMSource(host._decoder_cmd(tools.device_input_args(device), True),
                            host.chunk_bytes, True, title=device)
        src.start()
        return src
