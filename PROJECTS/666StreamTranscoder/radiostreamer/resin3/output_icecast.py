"""Icecast 2 / AzuraCast output adapter."""
from ..protocol import open_source_connection


def connect(cfg, timeout=10):
    if cfg.get("server_type") != "Icecast 2":
        raise ValueError("Icecast output adapter requires server_type='Icecast 2'.")
    return open_source_connection(cfg, timeout=timeout)
