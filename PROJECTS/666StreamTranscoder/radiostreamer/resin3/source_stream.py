"""Validated HTTP(S) input adapter for radio relay sources."""
from urllib.parse import urlparse
from .. import media


def stream_input_args(url):
    value = str(url or "").strip()
    parsed = urlparse(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("Relay source must be a complete HTTP or HTTPS URL.")
    return media.stream_input_args(value)


def display_name(url):
    parsed = urlparse(str(url or "").strip())
    return parsed.netloc or "Internet radio stream"
