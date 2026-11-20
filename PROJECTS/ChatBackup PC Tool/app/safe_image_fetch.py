"""Network boundary for untrusted chat image URLs.

Every connection resolves and pins a public IP; redirects and proxies are disabled.
No authentication information or original chat URL is forwarded.
"""
from __future__ import annotations

import http.client
import io
import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, UnidentifiedImageError

from chatbackup_core import ChatBackupError, USER_AGENT

_ALLOWED_FORMATS = {"PNG", "JPEG", "GIF", "WEBP", "BMP", "AVIF"}


def _public_address(hostname: str, port: int) -> str:
    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError) as exc:
        raise ChatBackupError("Bildserver konnte nicht sicher aufgelöst werden.") from exc
    if not infos:
        raise ChatBackupError("Bildserver hat keine IP-Adresse.")
    addresses = [info[4][0] for info in infos]
    try:
        if any(not ipaddress.ip_address(addr).is_global for addr in addresses):
            raise ChatBackupError("Private oder reservierte Bildserver-Adresse blockiert.")
    except ValueError as exc:
        raise ChatBackupError("Ungültige Bildserver-Adresse.") from exc
    return addresses[0]


def _checked_socket(host: str, port: int, timeout: object) -> socket.socket:
    address = _public_address(host, port)
    # Connect to the checked IP, not a second DNS lookup (rebinding protection).
    return socket.create_connection((address, port), timeout=timeout)


class _PinnedHTTP(http.client.HTTPConnection):
    def connect(self) -> None:
        self.sock = _checked_socket(self.host, self.port, self.timeout)


class _PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self) -> None:
        self.sock = _checked_socket(self.host, self.port, self.timeout)
        try:
            self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)
        except Exception:
            self.sock.close()
            raise


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ChatBackupError("Bildserver-Weiterleitungen sind aus Sicherheitsgründen deaktiviert.")


def _validate_url(url: str) -> str:
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise ChatBackupError("Ungültige Bild-URL.") from exc
    if (parts.scheme.lower() not in ("http", "https") or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.fragment or any(ord(ch) < 32 for ch in url)
            or (port is not None and port not in (80, 443))):
        raise ChatBackupError("Nicht zugelassene Bild-URL.")
    if parts.scheme == "https" and port not in (None, 443):
        raise ChatBackupError("Nicht zugelassener HTTPS-Port.")
    if parts.scheme == "http" and port not in (None, 80):
        raise ChatBackupError("Nicht zugelassener HTTP-Port.")
    return url


def fetch_chat_image(url: str, *, max_bytes: int = 30 * 1024 * 1024) -> tuple[bytes, str]:
    _validate_url(url)
    if max_bytes <= 0 or max_bytes > 30 * 1024 * 1024:
        raise ChatBackupError("Ungültige Bildgrößenbegrenzung.")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(),
        _NoRedirect(),
    )
    # Override only the transport, keeping urllib's existing HTTP behavior.
    opener.add_handler(_SafeHTTPHandler())
    opener.add_handler(_SafeHTTPSHandler())
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "image/png,image/jpeg,image/gif,image/webp,image/bmp,image/avif",
    }, method="GET")
    try:
        with opener.open(request, timeout=30) as response:
            mime = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if not mime.startswith("image/") or mime in ("image/svg+xml", "image/svg"):
                raise ChatBackupError("Antwort ist kein unterstützter Bildinhalt.")
            declared = response.headers.get("Content-Length")
            if declared:
                try:
                    if int(declared) > max_bytes:
                        raise ChatBackupError("Bilddatei überschreitet die Größengrenze.")
                except ValueError as exc:
                    raise ChatBackupError("Ungültige Größenangabe des Bildservers.") from exc
            data = response.read(max_bytes + 1)
    except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
        raise ChatBackupError("Bilddownload fehlgeschlagen (sichere Verbindung).") from exc
    if not data or len(data) > max_bytes:
        raise ChatBackupError("Bilddatei ist leer oder überschreitet die Größengrenze.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in _ALLOWED_FORMATS:
                raise ChatBackupError("Nicht unterstütztes Bildformat.")
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise ChatBackupError("Bilddatei konnte nicht verifiziert werden.") from exc
    return data, mime


class _SafeHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_PinnedHTTP, req)


class _SafeHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_PinnedHTTPS, req)
