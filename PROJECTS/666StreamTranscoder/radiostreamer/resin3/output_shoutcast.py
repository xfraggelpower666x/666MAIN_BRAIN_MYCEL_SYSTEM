"""Shoutcast v1/v2 output adapter."""
from ..protocol import open_source_connection


def connect(cfg, timeout=10):
    if not str(cfg.get("server_type", "")).startswith("Shoutcast"):
        raise ValueError("Shoutcast output adapter requires a Shoutcast server type.")
    return open_source_connection(cfg, timeout=timeout)
