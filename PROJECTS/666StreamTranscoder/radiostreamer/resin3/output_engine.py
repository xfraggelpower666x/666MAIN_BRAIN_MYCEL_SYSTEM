"""Resin 3 output boundary for the existing Shoutcast/Icecast connection adapters."""
from .output_router import connect


class OutputEngine:
    def __init__(self, cfg):
        self.cfg = dict(cfg)

    def open(self):
        return connect(self.cfg)

    @staticmethod
    def send(sock, encoded_bytes):
        sock.sendall(encoded_bytes)
        return len(encoded_bytes)

    @staticmethod
    def close(sock):
        if sock is None:
            return
        try:
            sock.shutdown(2)
        except OSError:
            pass
        sock.close()
