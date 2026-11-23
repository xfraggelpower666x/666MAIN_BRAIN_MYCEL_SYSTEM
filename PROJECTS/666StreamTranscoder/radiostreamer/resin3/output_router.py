"""Select the native output adapter without duplicating protocol implementation."""
from . import output_icecast, output_shoutcast


def connect(cfg, timeout=10):
    server_type = str(cfg.get("server_type", ""))
    if server_type == "Icecast 2":
        return output_icecast.connect(cfg, timeout=timeout)
    if server_type.startswith("Shoutcast"):
        return output_shoutcast.connect(cfg, timeout=timeout)
    raise ValueError(f"Unsupported output protocol: {server_type or '(empty)'}")
