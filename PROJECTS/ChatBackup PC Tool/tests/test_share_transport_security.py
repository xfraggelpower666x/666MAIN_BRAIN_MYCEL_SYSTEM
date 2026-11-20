"""Offline regressions for bounded, same-origin public share transport."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import chatbackup_core as core  # noqa: E402


class _Response:
    status = 200

    def __init__(self, payload: bytes, declared=None):
        self.payload = payload
        self.read_calls = []
        self.headers = self
        self.declared = declared

    def get(self, key, default=None):
        if key == "Content-Length":
            return self.declared
        return default

    def get_content_charset(self):
        return "utf-8"

    def read(self, size=-1):
        self.read_calls.append(size)
        return self.payload[:size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _opener(monkeypatch, response):
    class _Opener:
        def open(self, request, timeout):
            assert request.full_url == "https://chatgpt.com/share/example"
            return response

    monkeypatch.setattr(core.urllib.request, "build_opener", lambda *handlers: _Opener())


def test_html_fetch_is_bounded_and_valid_share_works(monkeypatch):
    response = _Response(b"<html>" + b"a" * 600 + b"</html>")
    _opener(monkeypatch, response)
    result = core.fetch_share_page("https://chatgpt.com/share/example")
    assert result.startswith("<html>")
    assert response.read_calls == [core.MAX_SHARE_HTML_BYTES + 1]


def test_content_length_rejects_oversize_before_read(monkeypatch):
    response = _Response(b"", str(core.MAX_SHARE_HTML_BYTES + 1))
    _opener(monkeypatch, response)
    with pytest.raises(core.ChatBackupError, match="Downloadlimit"):
        core.fetch_share_page("https://chatgpt.com/share/example")
    assert response.read_calls == []


def test_actual_oversize_rejected(monkeypatch):
    monkeypatch.setattr(core, "MAX_SHARE_HTML_BYTES", 512)
    response = _Response(b"x" * 513)
    _opener(monkeypatch, response)
    with pytest.raises(core.ChatBackupError, match="Downloadlimit"):
        core.fetch_share_page("https://chatgpt.com/share/example")
    assert response.read_calls == [513]


@pytest.mark.parametrize("bad_url", [
    "https://example.org/share/x", "https://chatgpt.com/c/private",
    "https://127.0.0.1/share/x", "http://evil.example/share/x",
    "https://chatgpt.com:8443/share/x",
])
def test_redirect_cannot_escape_public_share_origin(bad_url):
    handler = core._SafeShareRedirectHandler()
    req = core.urllib.request.Request("https://chatgpt.com/share/example")
    with pytest.raises(core.ChatBackupError):
        handler.redirect_request(req, None, 302, "Found", {}, bad_url)


def test_redirect_stays_on_public_share_origin():
    handler = core._SafeShareRedirectHandler()
    req = core.urllib.request.Request("https://chatgpt.com/share/example")
    redirected = handler.redirect_request(
        req, None, 302, "Found", {},
        "https://chatgpt.com/share/another",
    )
    assert redirected.full_url == "https://chatgpt.com/share/another"
