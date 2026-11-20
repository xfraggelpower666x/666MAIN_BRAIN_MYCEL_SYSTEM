"""Security regression for externally supplied chat image URLs.

All cases are offline. No network is contacted.
"""
import io
import socket
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
import safe_image_fetch as safe  # noqa: E402
from chatbackup_core import ChatBackupError  # noqa: E402


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "ftp://example.org/p.png", "https://user:pass@example.org/a.png",
    "http://example.org:8080/a.png", "https://example.org:8443/a.png",
    "http://example.org/a.png#frag", "https://example.org/\na.png",
])
def test_invalid_url_rejected_without_network(monkeypatch, url):
    monkeypatch.setattr(safe.socket, "getaddrinfo", lambda *a, **kw: pytest.fail("network called"))
    with pytest.raises(ChatBackupError):
        safe.fetch_chat_image(url)


@pytest.mark.parametrize("ip", [
    "127.0.0.1", "169.254.169.254", "10.0.0.1", "172.16.0.2",
    "192.168.1.1", "0.0.0.0", "::1", "fc00::1", "fe80::1",
])
def test_private_destinations_blocked(monkeypatch, ip):
    monkeypatch.setattr(safe.socket, "getaddrinfo", lambda *a, **kw: [
        (socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 0, "", (ip, 443))
    ])
    with pytest.raises(ChatBackupError):
        safe._public_address("untrusted.example", 443)


def test_mixed_dns_answers_fail_closed(monkeypatch):
    monkeypatch.setattr(safe.socket, "getaddrinfo", lambda *a, **kw: [
        (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("8.8.8.8", 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 443)),
    ])
    with pytest.raises(ChatBackupError):
        safe._public_address("example.org", 443)


def test_public_ip_is_pinned_before_connect(monkeypatch):
    calls = []
    monkeypatch.setattr(safe, "_public_address", lambda host, port: "8.8.8.8")
    monkeypatch.setattr(safe.socket, "create_connection", lambda address, timeout: calls.append((address, timeout)) or object())
    safe._checked_socket("cdn.example", 443, 12)
    assert calls == [(("8.8.8.8", 443), 12)]


def test_redirects_refused():
    with pytest.raises(ChatBackupError):
        safe._NoRedirect().redirect_request(None, None, 302, "found", {}, "http://127.0.0.1")


class _Response:
    def __init__(self, data, mime):
        self.data = data
        self.headers = {"Content-Type": mime, "Content-Length": str(len(data))}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, n):
        return self.data[:n]


def test_genuine_png_accepted_and_html_disguised_rejected(monkeypatch):
    buf = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    payload = buf.getvalue()
    class _Opener:
        def __init__(self):
            self.data = payload
            self.mime = "image/png"
        def open(self, request, timeout):
            return _Response(self.data, self.mime)
    opener = _Opener()
    monkeypatch.setattr(safe.urllib.request, "build_opener", lambda *handlers: opener)
    data, mime = safe.fetch_chat_image("https://cdn.example/image.png")
    assert data == payload and mime == "image/png"
    opener.data = b"<html>not an image</html>"
    with pytest.raises(ChatBackupError):
        safe.fetch_chat_image("https://cdn.example/fake.png")
    opener.mime = "text/html"
    with pytest.raises(ChatBackupError):
        safe.fetch_chat_image("https://cdn.example/fake.png")


def test_size_limit_enforced(monkeypatch):
    class _Opener:
        def open(self, request, timeout):
            return _Response(b"x" * 20, "image/png")
    monkeypatch.setattr(safe.urllib.request, "build_opener", lambda *handlers: _Opener())
    with pytest.raises(ChatBackupError):
        safe.fetch_chat_image("https://cdn.example/image.png", max_bytes=10)


def test_pinned_handlers_and_no_proxy():
    # Ensure a default, DNS-re-resolving HTTP handler cannot shadow the safe handler.
    assert safe._SafeHTTPHandler.__bases__ == (safe.urllib.request.HTTPHandler,)
    assert safe._SafeHTTPSHandler.__bases__ == (safe.urllib.request.HTTPSHandler,)
