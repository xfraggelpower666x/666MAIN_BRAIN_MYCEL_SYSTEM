"""Adapters for the preserved 3DX device, WASAPI loopback and app-capture sources."""
from .. import capture


def create_capture(source, cfg):
    if source == "loopback":
        return capture.LoopbackCapture(cfg.get("loopback_device", ""))
    if source == "app":
        return capture.AppCapture(cfg.get("app_name", ""))
    return None


def capture_format(source):
    if source == "app":
        return 48000, 2
    raise ValueError("Capture format is taken from the initialized device source.")
