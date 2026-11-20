from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit

APP_VERSION = "1.10.5"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/150.0.0.0 Safari/537.36"
)

CITATION_MARKER_RE = re.compile(
    r"(?:cite|filecite|navlist|filenavlist)[^]*"
)


@dataclass(slots=True)
class ExportStats:
    source_entries: int = 0
    exported: int = 0
    skipped_hidden: int = 0
    skipped_role: int = 0
    skipped_recipient: int = 0
    skipped_empty: int = 0
    skipped_duplicate: int = 0
    possibly_incomplete: int = 0
    copy_fields_detected: int = 0
    copy_fields_resolved: int = 0
    copy_fields_unresolved: int = 0

    @property
    def skipped_total(self) -> int:
        return (
            self.skipped_hidden
            + self.skipped_role
            + self.skipped_recipient
            + self.skipped_empty
        )

    @property
    def integrity_status(self) -> str:
        if self.possibly_incomplete or self.copy_fields_unresolved:
            return "WATCH"
        return "SOURCE-OK / UI-UNVERIFIED"


@dataclass(slots=True)
class ChatAsset:
    kind: str
    name: str
    mime_type: str = ""
    url: str = ""
    asset_pointer: str = ""
    source: str = "chat"


@dataclass(slots=True)
class CopyField:
    identifier: str
    label: str
    resolved: bool
    text: str | None = None
    utf16_length: int | None = None


@dataclass(slots=True)
class ChatParticipant:
    participant_id: str
    display_name: str
    role: str = "user"
    kind: str = "human"
    username: str = ""
    source: str = "structured"


@dataclass(slots=True)
class ChatMessage:
    role: str
    author: str
    text: str
    created_at: float | None = None
    assets: list[ChatAsset] = field(default_factory=list)
    message_id: str = ""
    content_type: str = ""
    status: str = ""
    recipient: str = "all"
    raw_content: dict[str, Any] = field(default_factory=dict)
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    copy_fields: list[CopyField] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    participant_id: str = ""
    participant_display_name: str = ""
    participant_kind: str = ""
    participant_username: str = ""
    participant_resolution: str = "UNRESOLVED"


@dataclass(slots=True)
class ChatBackup:
    title: str
    source_url: str
    share_id: str = "shared"
    model: str = ""
    updated_at: float | None = None
    messages: list[ChatMessage] = field(default_factory=list)
    parser: str = ""
    parser_details: str = ""
    warnings: list[str] = field(default_factory=list)
    stats: ExportStats = field(default_factory=ExportStats)
    parser_attempts: list[dict[str, Any]] = field(default_factory=list)
    primary_parser_error: str = ""
    source_html: str = ""
    source_html_sha256: str = ""
    source_html_chars: int = 0
    source_capture_status: str = "NOT_CAPTURED"
    participants: list[ChatParticipant] = field(default_factory=list)
    conversation_type: str = "single_or_unknown"
    group_chat_evidence: list[str] = field(default_factory=list)

    @property
    def is_group_chat(self) -> bool:
        return self.conversation_type == "group"

    def integrity_profile(self) -> dict[str, Any]:
        copy_status = (
            "UI_BINDINGS_PARTIAL" if self.stats.copy_fields_unresolved else
            "UI_BINDINGS_RESOLVED" if self.stats.copy_fields_resolved else
            "UI_BINDINGS_NOT_DETECTED"
        )
        image_assets = [a for m in self.messages for a in m.assets if a.kind == "image"]
        if not image_assets:
            asset_status = "ASSETS_NONE"
        elif all(a.url for a in image_assets):
            asset_status = "ASSETS_RESOLVED"
        else:
            asset_status = "ASSETS_PARTIAL"
        if self.parser == "manual-transcript":
            source_status = "MANUAL_STRUCTURED" if len(self.messages) > 1 else "MANUAL_PRESERVED"
        elif self.parser == "browser-assisted-transcript":
            source_status = "BROWSER_ASSISTED_RECOVERY"
        else:
            source_status = "DOM_FALLBACK" if "dom" in self.parser else (
                "SOURCE_WATCH" if self.stats.possibly_incomplete else "SOURCE_OK"
            )
        return {
            "sourceStatus": source_status,
            "rawPreservation": "RAW_PRESERVED" if self.source_html else self.source_capture_status,
            "uiBindings": copy_status,
            "assets": asset_status,
            "visualParity": "NOT_CLAIMED",
            "status": self.stats.integrity_status,
        }


class ChatBackupError(RuntimeError):
    """User-facing error while loading or parsing a backup."""


class AuthWallDetected(ChatBackupError):
    """The share URL returned a login/auth shell instead of conversation payload."""

    code = "AUTH_WALL_DETECTED"

    def __init__(self, message: str, *, source_url: str = "", evidence: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.source_url = source_url
        self.evidence = evidence or {}


def detect_auth_wall(page_html: str) -> dict[str, Any]:
    """Detect the current ChatGPT login shell without mistaking normal chat text for an auth wall.

    Detection is intentionally conservative: we require login UI evidence *and* absence of
    known conversation payload/DOM evidence. This turns a transport/product change into an
    explicit recovery state instead of a misleading parser-format error.
    """
    html = page_html or ""
    low = html.casefold()
    login_markers = [
        "log in or sign up",
        "continue with google",
        "continue with apple",
        "authstatus\":\"logged_out",
        'authstatus":"logged_out',
    ]
    payload_markers = [
        "linear_conversation",
        '"mapping"',
        "sharedconversationid",
        "conversation_id",
        "data-message-author-role",
        "data-conversation-transcript",
    ]
    login_hits = [marker for marker in login_markers if marker in low]
    payload_hits = [marker for marker in payload_markers if marker in low]
    detected = bool(login_hits) and not payload_hits
    return {
        "detected": detected,
        "status": "AUTH_WALL_DETECTED" if detected else "NO_AUTH_WALL",
        "loginMarkers": login_hits,
        "payloadMarkers": payload_hits,
        "htmlChars": len(html),
        "hasReactRouterStream": "streamcontroller.enqueue(" in low,
    }


def chat_asset_key(message_index: int, asset_index: int, asset: ChatAsset) -> str:
    """Return a stable machine-readable key for one structured chat asset."""
    raw = "\x1f".join(
        [
            str(message_index),
            str(asset_index),
            asset.kind or "",
            asset.name or "",
            asset.url or "",
            asset.asset_pointer or "",
            asset.source or "",
        ]
    )
    return "asset-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def normalize_and_validate_share_url(raw_url: str) -> str:
    url = str(raw_url or "").strip()
    if not url:
        raise ChatBackupError("Bitte einen ChatGPT-Share-Link eingeben.")

    url = re.sub(r"^http://", "https://", url, flags=re.IGNORECASE)
    url = url.split("#", 1)[0]

    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise ChatBackupError("Der eingegebene Link ist ungültig.") from exc

    # Reject userinfo, alternate schemes and ports before making an HTTP request.
    # A hostile ``user:pass@chatgpt.com`` URL must never be treated as a safe share.
    try:
        port = parsed.port
    except ValueError as exc:
        raise ChatBackupError("Der Share-Link enthält einen ungültigen Port.") from exc
    if (parsed.scheme.lower() not in {"http", "https"}
            or parsed.username is not None or parsed.password is not None
            or port not in (None, 443)
            or not parsed.hostname):
        raise ChatBackupError("Der Share-Link verwendet ein nicht unterstütztes URL-Format.")
    host = parsed.hostname.lower()
    if host not in {"chatgpt.com", "www.chatgpt.com", "chat.openai.com", "www.chat.openai.com"}:
        raise ChatBackupError("Der Link gehört nicht zu ChatGPT.")

    path = parsed.path or "/"
    if re.search(r"/c/", path, re.IGNORECASE):
        raise ChatBackupError(
            "Das ist ein privater Chat-Link (/c/...). Bitte im Chat über „Teilen“ "
            "einen öffentlichen Share-Link erstellen."
        )

    if not re.search(r"/(?:share|s)/", path, re.IGNORECASE):
        raise ChatBackupError(
            "Benötigt wird ein öffentlicher ChatGPT-Share-Link wie "
            "https://chatgpt.com/share/..."
        )

    return urlunsplit(("https", host, parsed.path, parsed.query, ""))


# Shared-page transport policy: only public ChatGPT shares, never arbitrary redirects.
MAX_SHARE_HTML_BYTES = 30 * 1024 * 1024


class _SafeShareRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Allow only same-origin public ChatGPT share redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        original = urlsplit(req.full_url)
        target = urlsplit(newurl)
        try:
            normalized = normalize_and_validate_share_url(newurl)
        except (ChatBackupError, ValueError) as exc:
            raise ChatBackupError("Unsichere Share-Weiterleitung blockiert.") from exc
        if (target.hostname or "").lower() != (original.hostname or "").lower():
            raise ChatBackupError("Domainwechsel bei Share-Weiterleitung blockiert.")
        return super().redirect_request(req, fp, code, msg, headers, normalized)


def fetch_share_page(
    url: str,
    timeout_seconds: int = 60,
    retries: int = 3,
) -> str:
    """Fetch a validated public share without unbounded reads or cross-domain redirects."""
    url = normalize_and_validate_share_url(url)
    opener = urllib.request.build_opener(_SafeShareRedirectHandler())
    last_error: Exception | None = None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        "Referer": "https://chatgpt.com/",
        "Cache-Control": "no-cache",
    }

    for attempt in range(1, max(1, retries) + 1):
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with opener.open(request, timeout=timeout_seconds) as response:
                status = getattr(response, "status", 200) or 200
                declared = response.headers.get("Content-Length")
                if declared:
                    try:
                        declared_size = int(declared)
                    except (TypeError, ValueError) as exc:
                        raise ChatBackupError("Ungültige Größenangabe der Share-Seite.") from exc
                    if declared_size < 0 or declared_size > MAX_SHARE_HTML_BYTES:
                        raise ChatBackupError("Die Share-Seite überschreitet das Downloadlimit.")
                body = response.read(MAX_SHARE_HTML_BYTES + 1)
                if len(body) > MAX_SHARE_HTML_BYTES:
                    raise ChatBackupError("Die Share-Seite überschreitet das Downloadlimit.")
                encoding = response.headers.get_content_charset() or "utf-8"
                text = body.decode(encoding, errors="replace")

            if status >= 400:
                raise ChatBackupError(
                    f"ChatGPT-Share-Seite konnte nicht geladen werden. HTTP {status}."
                )
            if len(text) < 500:
                raise ChatBackupError(
                    "Die ChatGPT-Share-Seite war leer oder unvollständig."
                )
            return text
        except urllib.error.HTTPError as exc:
            last_error = ChatBackupError(
                f"ChatGPT-Share-Seite konnte nicht geladen werden. HTTP {exc.code}."
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = ChatBackupError(f"Share-Netzwerkfehler: {exc}")
        except ChatBackupError as exc:
            # A deterministic safety rejection must never be hidden by retries.
            if "blockiert" in str(exc) or "Downloadlimit" in str(exc):
                raise
            last_error = exc
        except Exception as exc:  # pragma: no cover - defensive boundary
            last_error = exc

        if attempt < max(1, retries):
            time.sleep(attempt * 0.75)

    if isinstance(last_error, ChatBackupError):
        raise last_error
    raise ChatBackupError(str(last_error or "Unbekannter Downloadfehler."))


def load_chat_backup(
    url: str,
    *,
    preserve_raw_source: bool = True,
    max_raw_html_chars: int = 12_000_000,
) -> ChatBackup:
    normalized = normalize_and_validate_share_url(url)
    page = fetch_share_page(normalized)
    chat = parse_shared_conversation(page, normalized)
    enrich_chat_image_urls_from_html(chat, page)
    chat.source_html_chars = len(page)
    chat.source_html_sha256 = hashlib.sha256(page.encode("utf-8", errors="replace")).hexdigest()
    if preserve_raw_source and len(page) <= max(1, int(max_raw_html_chars)):
        chat.source_html = page
        chat.source_capture_status = "RAW_PRESERVED"
    elif preserve_raw_source:
        chat.source_capture_status = "RAW_TOO_LARGE_NOT_STORED"
        chat.warnings.append(
            f"Share-HTML ({len(page)} Zeichen) überschreitet das Raw-Capture-Limit von {max_raw_html_chars}."
        )
    else:
        chat.source_capture_status = "RAW_CAPTURE_DISABLED"
    return chat


def extract_public_image_url_candidates(page_html: str) -> list[str]:
    """Extract likely conversation-image URLs embedded in a public share page.

    The function is deliberately conservative: it does not associate arbitrary UI images
    with chat assets. Association is performed only later via a shared file/asset token.
    """
    normalized = html_lib.unescape(page_html or "")
    normalized = (
        normalized.replace("\\/", "/")
        .replace("\\u0026", "&")
        .replace("\\u003d", "=")
        .replace("\\u003D", "=")
    )
    candidates: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"https?://[^\s\"'<>]+", normalized, re.IGNORECASE):
        url = match.group(0).rstrip("),.;]")
        try:
            parsed = urlsplit(url)
        except ValueError:
            continue
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        looks_like_image = bool(re.search(r"\.(?:png|jpe?g|webp|gif|avif|bmp)(?:$|[?#])", url, re.IGNORECASE))
        trusted_asset_host = host.endswith("oaiusercontent.com") or host.endswith("openai.com") or host.endswith("chatgpt.com")
        assetish_path = any(token in path for token in ("/files/", "/file/", "/assets/", "backend-api"))
        if not ((trusted_asset_host and assetish_path) or looks_like_image):
            continue
        if url not in seen:
            seen.add(url)
            candidates.append(url)
    return candidates


def enrich_chat_image_urls_from_html(chat: ChatBackup, page_html: str) -> int:
    """Resolve pointer-only chat images when the same asset token occurs in an embedded URL."""
    candidates = extract_public_image_url_candidates(page_html)
    if not candidates:
        return 0
    enriched = 0
    for message in chat.messages:
        for asset in message.assets:
            if asset.kind != "image" or asset.url or not asset.asset_pointer:
                continue
            tokens = re.findall(r"(?:file|asset)-[A-Za-z0-9_-]+", asset.asset_pointer, re.IGNORECASE)
            matches = [url for url in candidates if any(token in url for token in tokens)]
            if len(matches) == 1:
                asset.url = matches[0]
                enriched += 1
    if enriched:
        chat.warnings.append(f"{enriched} Bild-URL(s) wurden über eingebettete Share-Asset-Tokens aufgelöst.")
    return enriched


def parse_shared_conversation(page_html: str, source_url: str) -> ChatBackup:
    auth_wall = detect_auth_wall(page_html)
    if auth_wall.get("detected"):
        raise AuthWallDetected(
            "ChatGPT hat für diesen Share-Link nur die Login-/Anmeldeoberfläche geliefert; "
            "der Gesprächspayload wurde dem direkten Abruf nicht bereitgestellt.",
            source_url=source_url,
            evidence=auth_wall,
        )

    attempts: list[dict[str, Any]] = []
    primary_error = ""

    loaders = extract_react_flight_loaders(page_html)
    for loader_index, loader in enumerate(loaders, start=1):
        try:
            decoded = decode_react_flight_loader(loader)
            route = find_share_route(decoded)
            if not route:
                attempts.append({"parser": "react-flight", "loader": loader_index, "status": "NO_ROUTE"})
                continue
            server_response = route.get("serverResponse") if isinstance(route, dict) else None
            server_response = server_response if isinstance(server_response, dict) else {}
            data = server_response.get("data")
            if not isinstance(data, dict):
                data = route.get("data") if isinstance(route, dict) else None
            if not isinstance(data, dict):
                data = {}
            chat = chat_from_data(data, route, source_url)
            chat.parser = "react-flight"
            chat.parser_details = f"React-Flight-Loader {loader_index}/{len(loaders)}"
            attempts.append({"parser": "react-flight", "loader": loader_index, "status": "PASS"})
            chat.parser_attempts = attempts
            chat.primary_parser_error = primary_error
            finalize_chat_stats(chat)
            return chat
        except Exception as exc:
            message = str(exc)
            if not primary_error:
                primary_error = message
            attempts.append({"parser": "react-flight", "loader": loader_index, "status": "FAIL", "error": message})

    try:
        legacy = extract_legacy_next_data(page_html)
        if legacy:
            chat = chat_from_data(legacy["data"], legacy["route"], source_url)
            chat.parser = "legacy-next-data"
            chat.parser_details = "Legacy __NEXT_DATA__"
            attempts.append({"parser": "legacy-next-data", "status": "PASS"})
            chat.parser_attempts = attempts
            chat.primary_parser_error = primary_error
            finalize_chat_stats(chat)
            return chat
        attempts.append({"parser": "legacy-next-data", "status": "NOT_PRESENT"})
    except Exception as exc:
        message = str(exc)
        if not primary_error:
            primary_error = message
        attempts.append({"parser": "legacy-next-data", "status": "FAIL", "error": message})

    try:
        chat = None
        if re.search(r"data-conversation-transcript", page_html, re.IGNORECASE):
            chat = extract_static_dom_conversation(page_html, source_url, ssr=True)
        if chat is None or not chat.messages:
            chat = extract_static_dom_conversation(page_html, source_url)
        if chat.messages:
            chat.warnings.append(
                "DOM-Fallback verwendet: Formatierungen, Links, UI-Bindungen oder Anhänge können unvollständig sein."
            )
            attempts.append({"parser": chat.parser, "status": "PASS"})
            chat.parser_attempts = attempts
            chat.primary_parser_error = primary_error
            finalize_chat_stats(chat)
            return chat
        attempts.append({"parser": "static-dom-fallback", "status": "NO_MESSAGES"})
    except Exception as exc:
        message = str(exc)
        if not primary_error:
            primary_error = message
        attempts.append({"parser": "static-dom-fallback", "status": "FAIL", "error": message})

    details = " | ".join(
        str(row.get("error")) for row in attempts if row.get("error")
    )[-1200:]
    suffix = f" Details: {details}" if details else ""
    raise ChatBackupError(
        "Im Share-Link wurden keine unterstützten Gesprächsdaten gefunden. "
        "Prüfe, ob der öffentliche Link noch gültig ist." + suffix
    )


def reparse_share_source(page_html: str, source_url: str) -> ChatBackup:
    """Re-run the current parser against a previously archived Share HTML snapshot."""
    chat = parse_shared_conversation(page_html, normalize_and_validate_share_url(source_url))
    enrich_chat_image_urls_from_html(chat, page_html)
    chat.source_html = page_html
    chat.source_html_chars = len(page_html)
    chat.source_html_sha256 = hashlib.sha256(page_html.encode("utf-8", errors="replace")).hexdigest()
    chat.source_capture_status = "RAW_PRESERVED_REPARSED"
    return chat

def extract_react_flight_loaders(page_html: str) -> list[list[Any]]:
    loaders: list[list[Any]] = []
    scripts = re.findall(r"<script\b[^>]*>([\s\S]*?)</script>", page_html, re.IGNORECASE)

    for script in scripts:
        for marker in ("streamController.enqueue(", "self.__next_f.push(", "__next_f.push("):
            start = 0
            while True:
                index = script.find(marker, start)
                if index < 0:
                    break
                arg_start = index + len(marker)
                literal = read_json_value_literal(script, arg_start)
                if literal is None:
                    start = arg_start + 1
                    continue
                raw_literal, end_index = literal
                start = end_index + 1
                try:
                    parsed_argument = json.loads(raw_literal)
                except json.JSONDecodeError:
                    continue

                candidates: list[Any] = []
                if isinstance(parsed_argument, str):
                    stripped = parsed_argument.strip()
                    if stripped.startswith("["):
                        try:
                            candidates.append(json.loads(stripped))
                        except json.JSONDecodeError:
                            pass
                else:
                    candidates.append(parsed_argument)

                for candidate in candidates:
                    if isinstance(candidate, list):
                        # __next_f commonly wraps the actual payload in [id, "..."]
                        if (
                            len(candidate) >= 2
                            and isinstance(candidate[1], str)
                            and candidate[1].lstrip().startswith("[")
                        ):
                            try:
                                nested = json.loads(candidate[1].strip())
                                if isinstance(nested, list):
                                    loaders.append(nested)
                            except json.JSONDecodeError:
                                pass
                        loaders.append(candidate)
    return loaders


def read_json_value_literal(text: str, start_index: int) -> tuple[str, int] | None:
    index = start_index
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return None

    first = text[index]
    if first == '"':
        escaped = False
        for pos in range(index + 1, len(text)):
            char = text[pos]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                return text[index : pos + 1], pos
        return None

    if first not in "[{":
        return None

    stack = [first]
    pairs = {"[": "]", "{": "}"}
    in_string = False
    escaped = False
    for pos in range(index + 1, len(text)):
        char = text[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            stack.append(char)
        elif char in "]}":
            if not stack or pairs[stack[-1]] != char:
                return None
            stack.pop()
            if not stack:
                return text[index : pos + 1], pos
    return None


def decode_react_flight_loader(loader: list[Any]) -> dict[str, Any]:
    cache: dict[int, Any] = {}
    resolving: set[int] = set()

    def decode_key(raw_key: Any) -> str:
        if isinstance(raw_key, str) and re.fullmatch(r"_\d+", raw_key):
            index = int(raw_key[1:])
            if 0 <= index < len(loader) and isinstance(loader[index], str):
                return loader[index]
        return str(raw_key)

    def resolve(value: Any) -> Any:
        if isinstance(value, int) and not isinstance(value, bool):
            if value in cache:
                return cache[value]
            if not 0 <= value < len(loader):
                return value
            if value in resolving:
                return None
            resolving.add(value)
            resolved = resolve(loader[value])
            resolving.remove(value)
            cache[value] = resolved
            return resolved
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if isinstance(value, dict):
            return {decode_key(key): resolve(item) for key, item in value.items()}
        return value

    decoded: dict[str, Any] = {}
    for index in range(1, len(loader) - 1, 2):
        key = loader[index]
        if isinstance(key, str) and key not in decoded:
            decoded[key] = resolve(loader[index + 1])
    return decoded


def find_share_route(decoded: Any) -> dict[str, Any] | None:
    if not isinstance(decoded, dict):
        return None

    loader_data = decoded.get("loaderData")
    if isinstance(loader_data, dict):
        for key in (
            "routes/share.$shareId.($action)",
            "routes/share.$shareId",
            "routes/s.$shareId.($action)",
            "routes/s.$shareId",
        ):
            route = loader_data.get(key)
            if isinstance(route, dict):
                return route

    seen: set[int] = set()

    def search(value: Any, depth: int) -> dict[str, Any] | None:
        if depth > 12 or not isinstance(value, (dict, list)):
            return None
        marker = id(value)
        if marker in seen:
            return None
        seen.add(marker)

        if isinstance(value, dict):
            direct_data = value.get("data")
            server = value.get("serverResponse")
            server_data = server.get("data") if isinstance(server, dict) else None
            if looks_like_conversation_data(direct_data) or looks_like_conversation_data(server_data):
                return value
            children: Iterable[Any] = value.values()
        else:
            children = value

        for child in children:
            found = search(child, depth + 1)
            if found:
                return found
        return None

    return search(decoded, 0)


def looks_like_conversation_data(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("mapping"), dict)
        and isinstance(value.get("linear_conversation"), list)
    )


def extract_legacy_next_data(page_html: str) -> dict[str, Any] | None:
    match = re.search(
        r"<script\b[^>]*id=[\"']__NEXT_DATA__[\"'][^>]*>([\s\S]*?)</script>",
        page_html,
        re.IGNORECASE,
    )
    if not match:
        return None
    payload = json.loads(html_lib.unescape(match.group(1)))
    props = payload.get("props") if isinstance(payload, dict) else None
    props = props if isinstance(props, dict) else {}
    page_props = props.get("pageProps")
    page_props = page_props if isinstance(page_props, dict) else {}
    server = page_props.get("serverResponse")
    server = server if isinstance(server, dict) else {}
    data = server.get("data")
    data = data if isinstance(data, dict) else {}
    return {
        "route": {
            "sharedConversationId": data.get("conversation_id", "shared"),
            "serverResponse": {"data": data},
        },
        "data": data,
    }


def _first_explicit_string(source: Any, keys: tuple[str, ...]) -> str:
    if not isinstance(source, dict):
        return ""
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _identity_name(value: str, role: str = "") -> str:
    """Keep explicit human/assistant display names, but ignore generic role placeholders."""
    text = str(value or "").strip()
    if not text:
        return ""
    low = text.casefold()
    generic = {"user", "human", "member", "participant", "assistant", "bot", "ai", "system", "developer", "tool"}
    if low in generic:
        return ""
    if role == "user" and low in {"you", "du", "benutzer"}:
        return ""
    return text


def _participant_from_record(record: Any, fallback_id: str = "", source: str = "structured") -> ChatParticipant | None:
    if not isinstance(record, dict):
        return None
    participant_id = _first_explicit_string(record, ("participant_id", "participantId", "id", "user_id", "userId", "account_id", "accountId")) or fallback_id
    role = (_first_explicit_string(record, ("role", "participant_role", "participantRole")) or "user").lower()
    raw_display_name = _first_explicit_string(record, ("display_name", "displayName", "name", "profile_name", "profileName", "username", "user_name", "userName"))
    display_name = _identity_name(raw_display_name, role)
    username = _first_explicit_string(record, ("username", "user_name", "userName", "handle"))
    kind = _first_explicit_string(record, ("kind", "type", "participant_type", "participantType"))
    low = (kind or role).lower()
    if not kind:
        kind = "assistant" if role == "assistant" else "human"
    elif any(token in low for token in ("assistant", "bot", "chatgpt", "ai")):
        kind = "assistant"
    else:
        kind = "human"
    if not participant_id and not display_name and not username:
        return None
    return ChatParticipant(
        participant_id=participant_id,
        display_name=display_name or username or participant_id,
        role=role,
        kind=kind,
        username=username,
        source=source,
    )


def _extract_participant_directory(data: dict[str, Any]) -> list[ChatParticipant]:
    """Extract only explicitly delivered participant/member records. No identity guessing."""
    containers: list[tuple[Any, str]] = []
    for key in ("participants", "members", "participant_profiles", "participantProfiles", "collaborators"):
        if key in data:
            containers.append((data.get(key), f"data.{key}"))
    for group_key in ("group", "group_chat", "groupChat"):
        group = data.get(group_key)
        if isinstance(group, dict):
            for key in ("participants", "members", "participant_profiles", "participantProfiles"):
                if key in group:
                    containers.append((group.get(key), f"data.{group_key}.{key}"))

    result: list[ChatParticipant] = []
    index_by_identity: dict[str, int] = {}
    for container, source in containers:
        if isinstance(container, dict):
            iterable = [(str(k), v) for k, v in container.items()]
        elif isinstance(container, list):
            iterable = [("", v) for v in container]
        else:
            continue
        for fallback_id, record in iterable:
            participant = _participant_from_record(record, fallback_id=fallback_id, source=source)
            if participant is None:
                continue
            identity = ("id:" + participant.participant_id.casefold()) if participant.participant_id else ("name:" + participant.display_name.casefold())
            if identity in index_by_identity:
                existing = result[index_by_identity[identity]]
                if not existing.display_name and participant.display_name:
                    existing.display_name = participant.display_name
                if not existing.username and participant.username:
                    existing.username = participant.username
                if existing.kind == "human" and participant.kind == "assistant":
                    existing.kind = "assistant"
                    existing.role = "assistant"
                continue
            index_by_identity[identity] = len(result)
            result.append(participant)
    return result


def _participant_lookup(participants: list[ChatParticipant]) -> tuple[dict[str, ChatParticipant], dict[str, ChatParticipant]]:
    by_id: dict[str, ChatParticipant] = {}
    by_name: dict[str, ChatParticipant] = {}
    for participant in participants:
        if participant.participant_id:
            by_id[participant.participant_id.casefold()] = participant
        for value in (participant.display_name, participant.username):
            if value:
                by_name[value.casefold()] = participant
    return by_id, by_name


def _resolve_message_participant(
    message: dict[str, Any],
    author: dict[str, Any],
    metadata: dict[str, Any],
    participants: list[ChatParticipant],
    role: str,
) -> tuple[str, str, str, str, str]:
    by_id, by_name = _participant_lookup(participants)
    participant_id = _first_explicit_string(author, ("participant_id", "participantId", "id", "user_id", "userId"))
    if not participant_id:
        participant_id = _first_explicit_string(metadata, ("participant_id", "participantId", "author_id", "authorId", "sender_id", "senderId", "user_id", "userId"))
    raw_display_name = _first_explicit_string(author, ("display_name", "displayName", "name", "profile_name", "profileName", "username", "user_name", "userName"))
    if not raw_display_name:
        raw_display_name = _first_explicit_string(metadata, ("participant_name", "participantName", "sender_name", "senderName", "author_name", "authorName", "display_name", "displayName", "username", "user_name", "userName"))
    display_name = _identity_name(raw_display_name, role)
    username = _first_explicit_string(author, ("username", "user_name", "userName", "handle")) or _first_explicit_string(metadata, ("username", "user_name", "userName", "handle"))

    participant = by_id.get(participant_id.casefold()) if participant_id else None
    if participant is None and display_name:
        participant = by_name.get(display_name.casefold())
    if participant is not None:
        return (
            participant.participant_id or participant_id,
            participant.display_name or display_name or author_name_for_role(role),
            participant.kind or ("assistant" if role == "assistant" else "human"),
            participant.username or username,
            "DIRECTORY_MATCH",
        )
    if participant_id or display_name or username:
        return (
            participant_id,
            display_name or username or participant_id or author_name_for_role(role),
            "assistant" if role == "assistant" else "human" if role == "user" else role,
            username,
            "MESSAGE_EXPLICIT",
        )
    if role == "assistant":
        return "chatgpt", "ChatGPT", "assistant", "", "ROLE_EXPLICIT"
    return "", author_name_for_role(role), "human" if role == "user" else role, "", "UNRESOLVED"


def _participant_to_dict(participant: ChatParticipant) -> dict[str, Any]:
    return {
        "participantId": participant.participant_id or None,
        "displayName": participant.display_name,
        "role": participant.role,
        "kind": participant.kind,
        "username": participant.username or None,
        "source": participant.source,
    }


def _finalize_group_chat_identity(chat: ChatBackup, data: dict[str, Any] | None = None) -> None:
    """Derive group status from explicit metadata or multiple explicit human identities."""
    data = data if isinstance(data, dict) else {}
    evidence: list[str] = []
    explicit_type = _first_explicit_string(data, ("conversation_type", "conversationType", "chat_type", "chatType", "type"))
    if data.get("is_group_chat") is True or data.get("isGroupChat") is True:
        evidence.append("EXPLICIT_GROUP_FLAG")
    if explicit_type and "group" in explicit_type.casefold():
        evidence.append(f"CONVERSATION_TYPE:{explicit_type}")
    if _first_explicit_string(data, ("group_id", "groupId")):
        evidence.append("GROUP_ID_PRESENT")

    humans: dict[str, ChatParticipant] = {}
    assistants: dict[str, ChatParticipant] = {}

    def add_participant(participant: ChatParticipant) -> None:
        target = assistants if participant.kind == "assistant" or participant.role == "assistant" else humans
        key = participant.participant_id.casefold() if participant.participant_id else participant.display_name.casefold()
        if key and key not in target:
            target[key] = participant

    for participant in chat.participants:
        add_participant(participant)

    for message in chat.messages:
        if message.participant_resolution == "UNRESOLVED":
            continue
        participant = ChatParticipant(
            participant_id=message.participant_id,
            display_name=message.participant_display_name or message.author,
            role=message.role,
            kind=message.participant_kind or ("assistant" if message.role == "assistant" else "human"),
            username=message.participant_username,
            source="message",
        )
        add_participant(participant)

    if len(humans) >= 2:
        evidence.append(f"MULTIPLE_EXPLICIT_HUMANS:{len(humans)}")

    if not assistants and any(message.role == "assistant" for message in chat.messages):
        assistants["chatgpt"] = ChatParticipant("chatgpt", "ChatGPT", role="assistant", kind="assistant", source="role")

    chat.participants = list(humans.values()) + list(assistants.values())
    chat.group_chat_evidence = evidence
    chat.conversation_type = "group" if evidence else "single_or_unknown"

def chat_from_data(data: dict[str, Any], route: dict[str, Any], source_url: str) -> ChatBackup:
    if not isinstance(data, dict):
        raise ChatBackupError("Keine Gesprächsdaten im Share-Link.")

    mapping = data.get("mapping") if isinstance(data.get("mapping"), dict) else {}
    sequence = data.get("linear_conversation") if isinstance(data.get("linear_conversation"), list) else []
    stats = ExportStats(source_entries=len(sequence))
    messages: list[ChatMessage] = []
    seen_ids: set[str] = set()
    participant_directory = _extract_participant_directory(data)

    for entry in sequence:
        node: dict[str, Any] | None = None
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            candidate = mapping.get(entry["id"])
            if isinstance(candidate, dict):
                node = candidate
        if node is None and isinstance(entry, dict) and isinstance(entry.get("message"), dict):
            node = entry
        if not isinstance(node, dict) or not isinstance(node.get("message"), dict):
            stats.skipped_empty += 1
            continue

        message = node["message"]
        metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
        if metadata.get("is_visually_hidden_from_conversation") is True:
            stats.skipped_hidden += 1
            continue

        author = message.get("author") if isinstance(message.get("author"), dict) else {}
        role = author.get("role") if isinstance(author.get("role"), str) else "assistant"
        if role in {"system", "developer", "tool"}:
            stats.skipped_role += 1
            continue

        recipient = message.get("recipient") if isinstance(message.get("recipient"), str) else "all"
        if role == "assistant" and recipient not in {"all", ""}:
            stats.skipped_recipient += 1
            continue

        message_id = message.get("id") if isinstance(message.get("id"), str) else ""
        if message_id and message_id in seen_ids:
            stats.skipped_duplicate += 1
            continue

        content = message.get("content") if isinstance(message.get("content"), dict) else {}
        content_type = content.get("content_type") if isinstance(content.get("content_type"), str) else ""
        assets = extract_message_assets(content, message)
        raw_text = flatten_message_content(content, message).strip()
        if not raw_text and assets:
            raw_text = "\n".join(asset_markdown_placeholder(asset) for asset in assets)
        if not raw_text:
            stats.skipped_empty += 1
            continue

        if message_id:
            seen_ids.add(message_id)

        copy_result = extract_copy_fields(raw_text)
        copy_fields = copy_result["fields"]
        message_warnings = list(copy_result["warnings"])
        stats.copy_fields_detected += len(copy_fields)
        stats.copy_fields_resolved += sum(1 for item in copy_fields if item.resolved)
        stats.copy_fields_unresolved += sum(1 for item in copy_fields if not item.resolved)

        status = message.get("status") if isinstance(message.get("status"), str) else ""
        if role == "assistant" and status and status != "finished_successfully":
            stats.possibly_incomplete += 1
            message_warnings.append(f"Nachrichtenstatus: {status}")
        if has_unclosed_code_fence(raw_text):
            stats.possibly_incomplete += 1
            message_warnings.append("Nicht geschlossener Markdown-Codeblock erkannt.")

        created = message.get("create_time")
        created_at = float(created) if isinstance(created, (int, float)) else None
        participant_id, participant_name, participant_kind, participant_username, participant_resolution = _resolve_message_participant(
            message, author, metadata, participant_directory, role
        )
        messages.append(
            ChatMessage(
                role=role,
                author=participant_name,
                text=clean_export_text(raw_text),
                created_at=created_at,
                assets=assets,
                message_id=message_id,
                content_type=content_type,
                status=status,
                recipient=recipient,
                raw_content=_json_safe_clone(content),
                raw_metadata=_json_safe_clone(metadata),
                copy_fields=copy_fields,
                warnings=message_warnings,
                participant_id=participant_id,
                participant_display_name=participant_name,
                participant_kind=participant_kind,
                participant_username=participant_username,
                participant_resolution=participant_resolution,
            )
        )

    stats.exported = len(messages)
    model_data = data.get("model") if isinstance(data.get("model"), dict) else {}
    model = model_data.get("slug") if isinstance(model_data.get("slug"), str) else ""
    route_share_id = route.get("sharedConversationId") if isinstance(route, dict) else ""
    share_id = (
        route_share_id
        if isinstance(route_share_id, str) and route_share_id
        else data.get("conversation_id")
        if isinstance(data.get("conversation_id"), str)
        else extract_share_id(source_url) or "shared"
    )
    title = data.get("title") if isinstance(data.get("title"), str) else ""
    updated = data.get("update_time")

    chat = ChatBackup(
        title=title.strip() or "ChatGPT Gespräch",
        source_url=source_url,
        share_id=share_id,
        model=model,
        updated_at=float(updated) if isinstance(updated, (int, float)) else None,
        messages=messages,
        stats=stats,
        participants=participant_directory,
    )
    if not messages:
        raise ChatBackupError("Im Share-Link wurden keine sichtbaren Nachrichten gefunden.")
    _finalize_group_chat_identity(chat, data)
    return chat


def _json_safe_clone(value: Any) -> Any:
    """Detach parser data into a JSON-safe archive representation."""
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str))
    except (TypeError, ValueError):
        if isinstance(value, dict):
            return {str(k): _json_safe_clone(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_json_safe_clone(v) for v in value]
        return str(value)


def _utf16_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def read_js_string_literal(source: str, start: int) -> tuple[str, int, bool] | None:
    if start >= len(source) or source[start] not in {'`', '"', "'"}:
        return None
    quote = source[start]
    escaped = False
    dynamic = False
    out: list[str] = []
    i = start + 1
    while i < len(source):
        char = source[i]
        if escaped:
            translations = {"n": "\n", "r": "\r", "t": "\t", "`": "`", "\\": "\\", "$": "$", '"': '"', "'": "'"}
            out.append(translations.get(char, "\\" + char))
            escaped = False
            i += 1
            continue
        if char == "\\":
            escaped = True
            i += 1
            continue
        if quote == "`" and char == "$" and i + 1 < len(source) and source[i + 1] == "{":
            dynamic = True
        if char == quote:
            return "".join(out), i + 1, dynamic
        out.append(char)
        i += 1
    return None


def guess_copy_field_label(identifier: str, source: str, position: int) -> str:
    key = identifier.lower()
    if re.search(r"main|haupt", key):
        return "Haupteingabe"
    if re.search(r"extend|exttext", key):
        return "Extended"
    if "style" in key:
        return "Style"
    if re.search(r"lyric|structure", key):
        return "Lyrics / Structure"
    if re.search(r"title|titel", key):
        return "Title"
    nearby = source[max(0, position - 180) : min(len(source), position + 220)]
    for pattern, label in (
        (r"Haupteingabe|main prompt", "Haupteingabe"),
        (r"Extended", "Extended"),
        (r"Style", "Style"),
        (r"Lyrics|Structure", "Lyrics / Structure"),
        (r"Titel|Title", "Title"),
    ):
        if re.search(pattern, nearby, re.IGNORECASE):
            return label
    return "Unbekannt"


def extract_copy_fields(source: str) -> dict[str, Any]:
    """Statically resolve literal GenUI.copy identifiers without executing JavaScript."""
    text = str(source or "")
    literals: dict[str, str] = {}
    dynamic_identifiers: set[str] = set()
    warnings: list[str] = []
    decl = re.compile(r"\b(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*")
    cursor = 0
    while True:
        match = decl.search(text, cursor)
        if not match:
            break
        cursor = match.end()
        literal = read_js_string_literal(text, cursor)
        if literal is None:
            continue
        value, end, dynamic = literal
        cursor = end
        if dynamic:
            dynamic_identifiers.add(match.group(1))
            warnings.append(f"Dynamischer Template-Ausdruck nicht statisch aufgelöst: {match.group(1)}")
        else:
            literals[match.group(1)] = value

    fields: list[CopyField] = []
    copied: set[str] = set()
    for match in re.finditer(r"GenUI\.copy\s*\(\s*([A-Za-z_$][\w$]*)\s*\)", text):
        identifier = match.group(1)
        if identifier in copied:
            continue
        copied.add(identifier)
        value = literals.get(identifier)
        resolved = value is not None
        fields.append(
            CopyField(
                identifier=identifier,
                label=guess_copy_field_label(identifier, text, match.start()),
                resolved=resolved,
                text=value,
                utf16_length=_utf16_length(value) if value is not None else None,
            )
        )
        if not resolved and identifier not in dynamic_identifiers:
            warnings.append(f"Copy-Referenz nicht statisch aufgelöst: {identifier}")

    unresolved = sum(1 for item in fields if not item.resolved)
    if unresolved:
        warnings.append(f"{unresolved} Kopieraktion(en) konnten nicht statisch aufgelöst werden.")
    return {"fields": fields, "warnings": list(dict.fromkeys(warnings))}

def flatten_message_content(content: dict[str, Any], message: dict[str, Any]) -> str:
    content_type = content.get("content_type") if isinstance(content.get("content_type"), str) else ""
    chunks: list[str] = []

    if content_type == "text" or (not content_type and isinstance(content.get("parts"), list)):
        for part in content.get("parts", []):
            value = extract_text_part(part)
            if value:
                chunks.append(value)
    elif content_type == "code":
        language = content.get("language") if isinstance(content.get("language"), str) else ""
        if language == "unknown":
            language = ""
        code = content.get("text") if isinstance(content.get("text"), str) else ""
        code = code.rstrip()
        if code:
            chunks.append(f"```{language}\n{code}\n```")
    elif content_type == "reasoning_recap":
        recap = content.get("content") if isinstance(content.get("content"), str) else ""
        if recap.strip():
            chunks.append(f"_{recap.strip()}_")
    elif content_type == "thoughts":
        thoughts = content.get("thoughts") if isinstance(content.get("thoughts"), list) else []
        for thought in thoughts:
            if isinstance(thought, dict) and isinstance(thought.get("summary"), str):
                summary = thought["summary"].strip()
                if summary:
                    chunks.append(f"_{summary}_")
    elif content_type == "multimodal_text":
        parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        for part in parts:
            if isinstance(part, str):
                cleaned = clean_export_text(part)
                if cleaned:
                    chunks.append(cleaned)
                continue
            if not isinstance(part, dict):
                continue
            part_type = str(part.get("content_type") or part.get("type") or "")
            if part_type == "text":
                text_value = part.get("text")
                if isinstance(text_value, list):
                    for item in text_value:
                        if isinstance(item, str) and item.strip():
                            chunks.append(clean_export_text(item))
                elif isinstance(text_value, str) and text_value.strip():
                    chunks.append(clean_export_text(text_value))
            elif part_type in {"image_asset_pointer", "file"}:
                pointer = part.get("asset_pointer") if isinstance(part.get("asset_pointer"), str) else ""
                label = "Bild aus dem Originalchat" if part_type == "image_asset_pointer" else "Datei aus dem Originalchat"
                if re.match(r"^https?://", pointer, re.IGNORECASE):
                    chunks.append(f"![{label}]({pointer})" if part_type == "image_asset_pointer" else f"[{label}]({pointer})")
                else:
                    chunks.append(f"*[{label} – nicht direkt downloadbar]*")
    elif isinstance(content.get("text"), str):
        cleaned = clean_export_text(content["text"])
        if cleaned:
            chunks.append(cleaned)

    attachments = extract_attachment_markdown(message)
    if attachments:
        chunks.append("\n".join(attachments))
    return re.sub(r"\n{4,}", "\n\n\n", "\n\n".join(filter(None, chunks))).strip()


def asset_markdown_placeholder(asset: ChatAsset) -> str:
    label = escape_markdown_label(asset.name or ("Bild" if asset.kind == "image" else "Anhang"))
    if asset.url and re.match(r"^https?://", asset.url, re.IGNORECASE):
        return f"![{label}]({asset.url})" if asset.kind == "image" else f"[{label}]({asset.url})"
    pointer_note = " – Asset-Pointer maschinenlesbar erhalten" if asset.asset_pointer else ""
    kind_label = "Bild" if asset.kind == "image" else "Anhang"
    return f"*[{kind_label}: {label}{pointer_note} – nicht direkt downloadbar]*"


def extract_message_assets(content: dict[str, Any], message: dict[str, Any]) -> list[ChatAsset]:
    """Extract image/file metadata without requiring the asset to be publicly downloadable."""
    assets: list[ChatAsset] = []
    seen: set[tuple[str, str, str]] = set()

    def add_asset(*, kind: str, name: str, mime_type: str = "", url: str = "", asset_pointer: str = "", source: str) -> None:
        key = (kind, url or asset_pointer, name)
        if key in seen:
            return
        seen.add(key)
        assets.append(
            ChatAsset(
                kind=kind,
                name=name or ("Bild" if kind == "image" else "Anhang"),
                mime_type=mime_type,
                url=url,
                asset_pointer=asset_pointer,
                source=source,
            )
        )

    if str(content.get("content_type") or "") == "multimodal_text":
        parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        image_counter = 0
        file_counter = 0
        for part in parts:
            if not isinstance(part, dict):
                continue
            part_type = str(part.get("content_type") or part.get("type") or "")
            if part_type not in {"image_asset_pointer", "file"}:
                continue
            pointer = str(part.get("asset_pointer") or part.get("url") or "").strip()
            direct_url = pointer if re.match(r"^https?://", pointer, re.IGNORECASE) else str(part.get("download_url") or "").strip()
            asset_pointer = "" if direct_url == pointer and direct_url else pointer
            if part_type == "image_asset_pointer":
                image_counter += 1
                name = str(part.get("name") or part.get("filename") or f"Chat-Bild-{image_counter}")
                mime = str(part.get("mime_type") or "image/*")
                add_asset(kind="image", name=name, mime_type=mime, url=direct_url, asset_pointer=asset_pointer, source="multimodal")
            else:
                file_counter += 1
                name = str(part.get("name") or part.get("filename") or f"Chat-Datei-{file_counter}")
                mime = str(part.get("mime_type") or "")
                kind = "image" if mime.lower().startswith("image/") else "file"
                add_asset(kind=kind, name=name, mime_type=mime, url=direct_url, asset_pointer=asset_pointer, source="multimodal")

    metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
    attachments = metadata.get("attachments") if isinstance(metadata.get("attachments"), list) else []
    for index, attachment in enumerate(attachments, start=1):
        if not isinstance(attachment, dict):
            continue
        url = str(attachment.get("download_url") or attachment.get("file_url") or attachment.get("url") or "").strip()
        pointer = str(attachment.get("asset_pointer") or attachment.get("id") or "").strip()
        name = str(attachment.get("name") or attachment.get("file_name") or f"Anhang-{index}").strip()
        mime = str(attachment.get("mime_type") or attachment.get("content_type") or "")
        kind = "image" if mime.lower().startswith("image/") else "file"
        add_asset(kind=kind, name=name, mime_type=mime, url=url, asset_pointer=pointer, source="attachment")

    return assets


def extract_text_part(part: Any) -> str:
    if isinstance(part, str):
        cleaned = clean_export_text(part)
        trimmed = cleaned.strip()
        if trimmed.startswith("{") and trimmed.endswith("}"):
            try:
                parsed = json.loads(trimmed)
                if isinstance(parsed, dict):
                    for key in ("response", "content"):
                        value = parsed.get(key)
                        if isinstance(value, str):
                            return clean_export_text(value)
            except json.JSONDecodeError:
                pass
        return cleaned
    if isinstance(part, dict):
        text = part.get("text")
        if isinstance(text, str):
            return clean_export_text(text)
        if isinstance(text, list):
            return "\n".join(
                clean_export_text(item)
                for item in text
                if isinstance(item, str) and clean_export_text(item)
            )
    return ""


def extract_attachment_markdown(message: dict[str, Any]) -> list[str]:
    metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
    attachments = metadata.get("attachments") if isinstance(metadata.get("attachments"), list) else []
    result: list[str] = []
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        url = attachment.get("download_url") or attachment.get("file_url") or ""
        name = str(attachment.get("name") or "Anhang").strip() or "Anhang"
        mime = str(attachment.get("mime_type") or "")
        label = escape_markdown_label(name)
        if isinstance(url, str) and re.match(r"^https?://", url, re.IGNORECASE):
            result.append(f"![{label}]({url})" if mime.lower().startswith("image/") else f"[{label}]({url})")
        else:
            result.append(f"*[Anhang: {label} – nicht direkt downloadbar]*")
    return result


def clean_export_text(text: Any) -> str:
    output = str(text or "")
    output = re.sub(r"[\uE000-\uF8FF]", "", output)
    output = output.replace("\x00", "")
    output = CITATION_MARKER_RE.sub("", output)
    output = re.sub(r"[ \t]+\n", "\n", output)
    output = re.sub(r"\n{4,}", "\n\n\n", output)
    return output.strip()



def analyze_manual_transcript(text: str, *, title: str = "Manual Chat Import") -> ChatBackup:
    """Best-effort structure recovery for private/single/group chat text copied from ChatGPT.

    Explicit ChatGPT role markers are supported in German/English. Free-form names are
    accepted as participants only from explicit ``Name:`` speaker lines. Markdown
    ``## Name`` headings are accepted only in transcript-like positions (document start
    or directly after ``---``), preventing ordinary response headings from becoming
    fake participants. Code fences are respected and identities are never guessed.
    """
    source = str(text or "").replace("\u0000", "")
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    known_user = {"you", "you said", "user", "benutzer", "du"}
    known_assistant = {"chatgpt", "chatgpt said", "assistant", "assistent"}
    colon_re = re.compile(r"^([A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9 ._'-]{0,48})(?:\s+said)?\s*:\s*$")
    heading_re = re.compile(r"^#{1,3}\s+([A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9 ._'-]{0,48})\s*$")
    excluded_generic = {
        "title", "titel", "status", "source", "quelle", "warning", "warnung", "note", "hinweis",
        "json", "markdown", "text", "code", "input", "output", "result", "ergebnis", "example", "beispiel",
        "introduction", "einleitung", "summary", "zusammenfassung", "details", "help", "hilfe",
    }

    def label_info(line: str) -> tuple[str, str] | None:
        stripped = line.strip()
        m = colon_re.match(stripped)
        if m:
            return m.group(1).strip(), "colon"
        m = heading_re.match(stripped)
        if m:
            return m.group(1).strip(), "heading"
        clean = re.sub(r"^#{1,3}\s*", "", stripped).rstrip(":").strip()
        low = clean.casefold()
        if low in known_user or low in known_assistant:
            return clean, "known"
        return None

    lines = normalized.split("\n")
    candidate_labels: list[str] = []
    allowed_heading_labels: set[str] = set()
    in_fence = False
    previous_significant = ""
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            previous_significant = line.strip()
            continue
        if in_fence:
            if line.strip():
                previous_significant = line.strip()
            continue
        info = label_info(line)
        if info:
            label, style = info
            low = label.casefold()
            if low not in known_user and low not in known_assistant and low not in excluded_generic:
                if style == "colon":
                    candidate_labels.append(label)
                elif style == "heading" and previous_significant == "---":
                    candidate_labels.append(label)
                    allowed_heading_labels.add(low)
        if line.strip():
            previous_significant = line.strip()

    generic_counts: dict[str, int] = {}
    canonical_generic: dict[str, str] = {}
    for label in candidate_labels:
        key = label.casefold()
        generic_counts[key] = generic_counts.get(key, 0) + 1
        canonical_generic.setdefault(key, label)
    group_generic_enabled = len(generic_counts) >= 2 and sum(generic_counts.values()) >= 2

    def marker_info(line: str, previous_nonempty: str) -> tuple[str, str, str, str, str] | None:
        info = label_info(line)
        if not info:
            return None
        label, style = info
        low = label.casefold()
        if low in known_user:
            return "user", "Benutzer", "manual-you", "human", "ROLE_MARKER"
        if low in known_assistant:
            return "assistant", "ChatGPT", "chatgpt", "assistant", "ROLE_MARKER"
        if group_generic_enabled and low in generic_counts:
            if style == "heading" and (low not in allowed_heading_labels or previous_nonempty != "---"):
                return None
            digest = hashlib.sha256(low.encode("utf-8")).hexdigest()[:12]
            return "user", canonical_generic[low], f"manual-participant-{digest}", "human", "EXPLICIT_SPEAKER_LABEL"
        return None

    blocks: list[tuple[str, str, str, str, str, list[str]]] = []
    current: tuple[str, str, str, str, str] | None = None
    current_lines: list[str] = []
    in_fence = False
    previous_nonempty = ""
    for line in lines:
        toggles_fence = line.lstrip().startswith("```")
        if toggles_fence:
            in_fence = not in_fence
            if current is not None:
                current_lines.append(line)
            previous_nonempty = line.strip()
            continue
        info = None if in_fence else marker_info(line, previous_nonempty)
        if info is not None:
            if current is not None:
                blocks.append((*current, current_lines))
            current = info
            current_lines = []
            previous_nonempty = line.strip()
            continue
        if current is not None:
            current_lines.append(line)
        if line.strip():
            previous_nonempty = line.strip()
    if current is not None:
        blocks.append((*current, current_lines))

    messages: list[ChatMessage] = []
    stats = ExportStats(source_entries=len(blocks) if blocks else 1)
    warnings: list[str] = []

    if len(blocks) >= 2:
        for index, (role, author, participant_id, participant_kind, participant_resolution, block_lines) in enumerate(blocks, start=1):
            body = "\n".join(block_lines).strip()
            if not body:
                stats.skipped_empty += 1
                continue
            copy_result = extract_copy_fields(body)
            copy_fields = copy_result["fields"]
            msg_warnings = list(copy_result["warnings"])
            stats.copy_fields_detected += len(copy_fields)
            stats.copy_fields_resolved += sum(1 for item in copy_fields if item.resolved)
            stats.copy_fields_unresolved += sum(1 for item in copy_fields if not item.resolved)
            if has_unclosed_code_fence(body):
                stats.possibly_incomplete += 1
                msg_warnings.append("Unclosed code fence detected in manually copied text.")
            messages.append(ChatMessage(
                role=role, author=author, text=body, message_id=f"manual-{index:04d}",
                content_type="manual_transcript", status="recovered_from_manual_copy",
                raw_content={"sourceText": body},
                raw_metadata={"manualImport": True, "roleMarkerRecovered": True, "participantLabelRecovered": participant_resolution == "EXPLICIT_SPEAKER_LABEL"},
                copy_fields=copy_fields, warnings=msg_warnings,
                participant_id=participant_id, participant_display_name=author,
                participant_kind=participant_kind, participant_resolution=participant_resolution,
            ))
        parser_details = f"Explicit role/participant marker recovery ({len(messages)} messages)"
    else:
        body = normalized.strip()
        if body:
            copy_result = extract_copy_fields(body)
            copy_fields = copy_result["fields"]
            stats.copy_fields_detected = len(copy_fields)
            stats.copy_fields_resolved = sum(1 for item in copy_fields if item.resolved)
            stats.copy_fields_unresolved = sum(1 for item in copy_fields if not item.resolved)
            messages.append(ChatMessage(
                role="manual", author="Manual Import", text=body, message_id="manual-0001",
                content_type="manual_unstructured", status="preserved_without_role_split",
                raw_content={"sourceText": body},
                raw_metadata={"manualImport": True, "roleMarkerRecovered": False},
                copy_fields=copy_fields, warnings=list(copy_result["warnings"]),
                participant_resolution="UNRESOLVED",
            ))
        warnings.append("No reliable ChatGPT/participant markers were found. The paste was preserved as one message; no conversation turns or identities were invented.")
        parser_details = "Manual preservation fallback (no reliable role/participant markers)"

    chat = ChatBackup(
        title=title or "Manual Chat Import", source_url="manual://clipboard", share_id="manual",
        messages=messages, parser="manual-transcript", parser_details=parser_details,
        warnings=warnings, stats=stats, source_capture_status="MANUAL_TEXT_PRESERVED",
    )
    _finalize_group_chat_identity(chat, {})
    chat.parser_attempts = [{
        "parser": "manual-role-participant-marker",
        "status": "PASS" if len(blocks) >= 2 else "FALLBACK",
        "detectedBlocks": len(blocks),
        "genericParticipantMode": group_generic_enabled,
        "explicitHumanParticipants": len([p for p in chat.participants if p.kind == "human"]),
    }]
    finalize_chat_stats(chat)
    return chat

def finalize_chat_stats(chat: ChatBackup) -> None:
    chat.stats.exported = len(chat.messages)
    if chat.stats.possibly_incomplete > 0:
        warning = f"{chat.stats.possibly_incomplete} Nachricht(en) könnten unvollständig sein."
        if warning not in chat.warnings:
            chat.warnings.append(warning)
    if chat.stats.copy_fields_unresolved > 0:
        warning = f"{chat.stats.copy_fields_unresolved} Copy-/UI-Feld(er) konnten nicht statisch aufgelöst werden."
        if warning not in chat.warnings:
            chat.warnings.append(warning)


def build_markdown(chat: ChatBackup, include_integrity: bool = True) -> str:
    lines: list[str] = [f"# {sanitize_heading(chat.title)}", ""]
    lines.append(f"- **Quelle:** {chat.source_url}")
    lines.append(f"- **Exportiert:** {format_local_datetime(datetime.now())}")
    if chat.model:
        lines.append(f"- **Modell:** {chat.model}")
    if chat.updated_at:
        lines.append(f"- **Chat aktualisiert:** {format_unix_timestamp(chat.updated_at)}")
    lines.append(f"- **Nachrichten:** {len(chat.messages)}")
    if chat.is_group_chat:
        humans = [p for p in chat.participants if p.kind == "human"]
        lines.append(f"- **Gesprächstyp:** Gruppenchat")
        lines.append(f"- **Teilnehmende:** {len(humans)} menschlich + ChatGPT" if any(p.kind == "assistant" for p in chat.participants) else f"- **Teilnehmende:** {len(humans)} menschlich")
        if humans:
            lines.append("- **Teilnehmernamen:** " + ", ".join(p.display_name for p in humans))
    if chat.parser:
        lines.append(f"- **Parser:** {chat.parser}")
    if chat.parser_details:
        lines.append(f"- **Parser-Details:** {chat.parser_details}")
    for warning in chat.warnings:
        lines.append(f"- **Warnung:** {warning}")
    lines.extend(["", "---", ""])

    for index, message in enumerate(chat.messages):
        lines.append(f"## {message.author}")
        lines.append("")
        lines.append(message.text.strip())
        lines.append("")
        if message.copy_fields:
            lines.extend(["### Erkannte Copy-/UI-Felder", ""])
            for field_item in message.copy_fields:
                state = f"{field_item.utf16_length} UTF-16-Zeicheneinheiten" if field_item.resolved else "UNAUFGELÖST"
                lines.append(f"**{field_item.label}** (`{field_item.identifier}`) – {state}")
                if field_item.resolved and field_item.text is not None:
                    lines.extend(["", "```text", field_item.text, "```", ""])
            if message.warnings:
                for warning in message.warnings:
                    lines.append(f"- **Nachrichtenwarnung:** {warning}")
                lines.append("")
        if index < len(chat.messages) - 1:
            lines.extend(["---", ""])

    if include_integrity:
        append_integrity_section(lines, chat)

    return re.sub(r"\n{4,}", "\n\n\n", "\n".join(lines)).strip() + "\n"


def append_integrity_section(lines: list[str], chat: ChatBackup) -> None:
    stats = chat.stats
    profile = chat.integrity_profile()
    lines.extend(
        [
            "",
            "---",
            "",
            "## Export-Integrität",
            "",
            f"- **Quellsequenz:** {stats.source_entries}",
            f"- **Exportiert:** {stats.exported}",
            f"- **Übersprungen:** {stats.skipped_total}",
            f"- **Versteckt:** {stats.skipped_hidden}",
            f"- **Rollenfilter:** {stats.skipped_role}",
            f"- **Empfängerfilter:** {stats.skipped_recipient}",
            f"- **Leer/ungültig:** {stats.skipped_empty}",
            f"- **Duplikate:** {stats.skipped_duplicate}",
            f"- **Möglicherweise unvollständig:** {stats.possibly_incomplete}",
            f"- **Copy-/UI-Felder erkannt:** {stats.copy_fields_detected}",
            f"- **Copy-/UI-Felder aufgelöst:** {stats.copy_fields_resolved}",
            f"- **Copy-/UI-Felder offen:** {stats.copy_fields_unresolved}",
            f"- **Parser:** {chat.parser or 'unbekannt'}",
            f"- **Quellstatus:** {profile['sourceStatus']}",
            f"- **Raw-Quellerhalt:** {profile['rawPreservation']}",
            f"- **UI-Bindungen:** {profile['uiBindings']}",
            f"- **Assets:** {profile['assets']}",
            f"- **Visuelle Parität:** {profile['visualParity']}",
            f"- **Status:** {profile['status']}",
            "- **Hinweis:** Ein erfolgreicher Quellparser beweist keine pixelgenaue Rekonstruktion dynamischer ChatGPT-UI.",
            "",
            "=== EXPORT COMPLETE ===",
        ]
    )

def build_javascript_export(
    content: str,
    title: str,
    source_url: str = "",
    source_mode: str = "manual",
) -> str:
    payload = {
        "schemaVersion": "1.0.0",
        "tool": "666_CHATBACKUP_PC_TOOL",
        "toolVersion": APP_VERSION,
        "title": title or "ChatGPT Backup",
        "sourceMode": source_mode,
        "sourceUrl": source_url,
        "exportedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "content": content,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    encoded = encoded.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return (
        "/* Generated by 666_CHATBACKUP_PC_TOOL. */\n"
        f"const CHAT_BACKUP_EXPORT = Object.freeze({encoded});\n\n"
        "if (typeof module !== \"undefined\" && module.exports) {\n"
        "  module.exports = CHAT_BACKUP_EXPORT;\n"
        "}\n"
    )


def _asset_to_dict(
    asset: ChatAsset,
    *,
    message_index: int,
    asset_index: int,
    selected_asset_keys: set[str] | None = None,
) -> dict[str, Any]:
    key = chat_asset_key(message_index, asset_index, asset)
    selected = True if selected_asset_keys is None else (asset.kind != "image" or key in selected_asset_keys)
    return {
        "assetKey": key,
        "assetIndex": asset_index,
        "kind": asset.kind,
        "name": asset.name,
        "mimeType": asset.mime_type,
        "url": asset.url,
        "assetPointer": asset.asset_pointer,
        "source": asset.source,
        "downloadable": bool(asset.url and re.match(r"^https?://", asset.url, re.IGNORECASE)),
        "selectedForPortable": selected,
    }


def _copy_field_to_dict(field_item: CopyField) -> dict[str, Any]:
    return {
        "identifier": field_item.identifier,
        "label": field_item.label,
        "resolved": field_item.resolved,
        "text": field_item.text,
        "utf16Length": field_item.utf16_length,
    }


def build_machine_payload(
    *,
    content: str,
    title: str,
    source_url: str = "",
    source_mode: str = "manual",
    chat: ChatBackup | None = None,
    local_assets: list[dict[str, Any]] | None = None,
    selected_asset_keys: set[str] | None = None,
) -> dict[str, Any]:
    """Build the loss-aware machine export used for archive, re-import and analysis."""
    payload: dict[str, Any] = {
        "schema": "666.chatbackup.machine.v1",
        "schemaVersion": "1.3.0",
        "tool": "666_CHATBACKUP_PC_TOOL",
        "toolVersion": APP_VERSION,
        "exportedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "title": title or "ChatGPT Backup",
        "source": {
            "mode": source_mode,
            "url": source_url,
        },
        "renderedContent": content,
        "renderedContentSha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "messages": [],
        "assets": [],
        "assetSelection": {
            "mode": "all" if selected_asset_keys is None else "explicit",
            "selectedAssetKeys": sorted(selected_asset_keys) if selected_asset_keys is not None else None,
        },
    }

    if chat is not None:
        profile = chat.integrity_profile()
        payload["sourceCapture"] = {
            "status": chat.source_capture_status,
            "htmlChars": chat.source_html_chars,
            "htmlSha256": chat.source_html_sha256 or None,
            "rawHtmlEmbeddedInMachineJson": False,
            "parserAttempts": _json_safe_clone(chat.parser_attempts),
            "primaryParserError": chat.primary_parser_error or None,
            "reparseReady": bool(chat.source_html),
        }
        payload["conversation"] = {
            "shareId": chat.share_id,
            "model": chat.model,
            "updatedAt": format_unix_timestamp(chat.updated_at) if chat.updated_at else None,
            "parser": chat.parser,
            "parserDetails": chat.parser_details,
            "warnings": list(chat.warnings),
            "integrity": {
                **profile,
                "sourceEntries": chat.stats.source_entries,
                "exported": chat.stats.exported,
                "skippedTotal": chat.stats.skipped_total,
                "skippedHidden": chat.stats.skipped_hidden,
                "skippedRole": chat.stats.skipped_role,
                "skippedRecipient": chat.stats.skipped_recipient,
                "skippedEmpty": chat.stats.skipped_empty,
                "skippedDuplicate": chat.stats.skipped_duplicate,
                "possiblyIncomplete": chat.stats.possibly_incomplete,
                "copyFieldsDetected": chat.stats.copy_fields_detected,
                "copyFieldsResolved": chat.stats.copy_fields_resolved,
                "copyFieldsUnresolved": chat.stats.copy_fields_unresolved,
            },
            "structuredMessagesOrigin": "loaded-share-before-editor-edits"
            if source_mode == "share-link-edited"
            else "loaded-share",
            "conversationType": chat.conversation_type,
            "isGroupChat": chat.is_group_chat,
            "groupChatEvidence": list(chat.group_chat_evidence),
            "participantCount": len(chat.participants),
            "participants": [_participant_to_dict(p) for p in chat.participants],
        }
        all_assets: list[dict[str, Any]] = []
        for index, message in enumerate(chat.messages, start=1):
            message_assets = [
                _asset_to_dict(
                    asset,
                    message_index=index,
                    asset_index=asset_index,
                    selected_asset_keys=selected_asset_keys,
                )
                for asset_index, asset in enumerate(message.assets, start=1)
            ]
            payload["messages"].append(
                {
                    "index": index,
                    "id": message.message_id or None,
                    "role": message.role,
                    "author": message.author,
                    "participantId": message.participant_id or None,
                    "participantDisplayName": message.participant_display_name or message.author,
                    "participantKind": message.participant_kind or None,
                    "participantUsername": message.participant_username or None,
                    "participantResolution": message.participant_resolution,
                    "recipient": message.recipient,
                    "status": message.status or None,
                    "createdAt": format_unix_timestamp(message.created_at) if message.created_at else None,
                    "contentType": message.content_type or None,
                    "text": message.text,
                    "renderedText": message.text,
                    "rawContent": _json_safe_clone(message.raw_content),
                    "rawMetadata": _json_safe_clone(message.raw_metadata),
                    "copyFields": [_copy_field_to_dict(item) for item in message.copy_fields],
                    "warnings": list(message.warnings),
                    "assets": message_assets,
                }
            )
            for asset in message_assets:
                all_assets.append({"messageIndex": index, **asset})
        payload["assets"] = all_assets
        image_assets = [row for row in all_assets if row.get("kind") == "image"]
        payload["assetSelection"].update(
            {
                "chatImageCount": len(image_assets),
                "selectedChatImageCount": sum(1 for row in image_assets if row.get("selectedForPortable")),
            }
        )
    else:
        payload["messages"] = [
            {
                "index": 1,
                "id": None,
                "role": "manual",
                "author": "Manueller Inhalt",
                "recipient": "all",
                "status": None,
                "createdAt": None,
                "contentType": "manual",
                "text": content,
                "renderedText": content,
                "rawContent": {"text": content},
                "rawMetadata": {},
                "copyFields": [],
                "warnings": [],
                "assets": [],
            }
        ] if content else []

    payload["localAssets"] = local_assets or []
    return payload


def build_raw_source_bundle(chat: ChatBackup) -> dict[str, Any]:
    """Archive parser-facing message source separately from the readable export."""
    return {
        "schema": "666.chatbackup.raw-source.v2",
        "version": 2,
        "toolVersion": APP_VERSION,
        "exportedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sourceUrl": chat.source_url,
        "shareId": chat.share_id,
        "title": chat.title,
        "conversationType": chat.conversation_type,
        "isGroupChat": chat.is_group_chat,
        "groupChatEvidence": list(chat.group_chat_evidence),
        "participants": [_participant_to_dict(p) for p in chat.participants],
        "parser": chat.parser,
        "parserDetails": chat.parser_details,
        "parserAttempts": _json_safe_clone(chat.parser_attempts),
        "primaryParserError": chat.primary_parser_error or None,
        "sourceCapture": {
            "status": chat.source_capture_status,
            "htmlChars": chat.source_html_chars,
            "htmlSha256": chat.source_html_sha256 or None,
        },
        "integrity": chat.integrity_profile(),
        "stats": {
            "sourceEntries": chat.stats.source_entries,
            "exported": chat.stats.exported,
            "skippedHidden": chat.stats.skipped_hidden,
            "skippedRole": chat.stats.skipped_role,
            "skippedRecipient": chat.stats.skipped_recipient,
            "skippedEmpty": chat.stats.skipped_empty,
            "skippedDuplicate": chat.stats.skipped_duplicate,
            "possiblyIncomplete": chat.stats.possibly_incomplete,
            "copyFieldsDetected": chat.stats.copy_fields_detected,
            "copyFieldsResolved": chat.stats.copy_fields_resolved,
            "copyFieldsUnresolved": chat.stats.copy_fields_unresolved,
        },
        "notes": [
            "Raw message content and rendered text are retained separately.",
            "Dynamic UI bindings are not executed.",
            "Source success does not claim pixel-perfect UI recovery.",
        ],
        "messages": [
            {
                "index": index,
                "id": message.message_id or None,
                "role": message.role,
                "author": message.author,
                "participantId": message.participant_id or None,
                "participantDisplayName": message.participant_display_name or message.author,
                "participantKind": message.participant_kind or None,
                "participantUsername": message.participant_username or None,
                "participantResolution": message.participant_resolution,
                "recipient": message.recipient,
                "status": message.status or None,
                "createdAtUnix": message.created_at,
                "contentType": message.content_type or None,
                "rawContent": _json_safe_clone(message.raw_content),
                "rawMetadata": _json_safe_clone(message.raw_metadata),
                "renderedText": message.text,
                "copyFields": [_copy_field_to_dict(item) for item in message.copy_fields],
                "warnings": list(message.warnings),
                "assets": [_asset_to_dict(asset, message_index=index, asset_index=aidx) for aidx, asset in enumerate(message.assets, 1)],
            }
            for index, message in enumerate(chat.messages, 1)
        ],
    }



def build_structure_inspector_payload(chat: ChatBackup) -> dict[str, Any]:
    """Return exactly the structured data exposed by the GUI structure inspector.

    This export is intentionally independent from the broader machine export so it
    can be archived, diffed and consumed as a stable inspector snapshot.
    """
    profile = chat.integrity_profile()
    messages: list[dict[str, Any]] = []
    for index, message in enumerate(chat.messages, 1):
        messages.append({
            "index": index,
            "id": message.message_id or None,
            "role": message.role,
            "author": message.author,
            "participantId": message.participant_id or None,
            "participantDisplayName": message.participant_display_name or message.author,
            "participantKind": message.participant_kind or None,
            "participantUsername": message.participant_username or None,
            "participantResolution": message.participant_resolution,
            "recipient": message.recipient,
            "status": message.status or None,
            "contentType": message.content_type or None,
            "createdAtUnix": message.created_at,
            "copyFields": [_copy_field_to_dict(item) for item in message.copy_fields],
            "warnings": list(message.warnings),
            "rawContent": _json_safe_clone(message.raw_content),
            "rawMetadata": _json_safe_clone(message.raw_metadata),
            "renderedText": message.text,
            "assets": [
                _asset_to_dict(asset, message_index=index, asset_index=aidx)
                for aidx, asset in enumerate(message.assets, 1)
            ],
        })
    return {
        "schema": "666.chatbackup.structure-inspector.v1",
        "schemaVersion": "1.1.0",
        "tool": "666_CHATBACKUP_PC_TOOL",
        "toolVersion": APP_VERSION,
        "exportedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "title": chat.title,
        "sourceUrl": chat.source_url,
        "shareId": chat.share_id,
        "summary": {
            "parser": chat.parser,
            "parserDetails": chat.parser_details,
            "messageCount": len(chat.messages),
            "conversationType": chat.conversation_type,
            "isGroupChat": chat.is_group_chat,
            "participantCount": len(chat.participants),
            "groupChatEvidence": list(chat.group_chat_evidence),
            "copyFieldsDetected": chat.stats.copy_fields_detected,
            "copyFieldsResolved": chat.stats.copy_fields_resolved,
            "copyFieldsUnresolved": chat.stats.copy_fields_unresolved,
            "rawPreservation": profile["rawPreservation"],
            "sourceHtmlChars": chat.source_html_chars,
            "sourceHtmlSha256": chat.source_html_sha256 or None,
            "visualParity": profile["visualParity"],
        },
        "integrity": profile,
        "participants": [_participant_to_dict(p) for p in chat.participants],
        "parserProvenance": {
            "attempts": _json_safe_clone(chat.parser_attempts),
            "primaryParserError": chat.primary_parser_error or None,
            "sourceCaptureStatus": chat.source_capture_status,
        },
        "messages": messages,
    }


def build_structure_inspector_json(chat: ChatBackup) -> str:
    return json.dumps(build_structure_inspector_payload(chat), ensure_ascii=False, indent=2) + "\n"

def build_parser_receipt(chat: ChatBackup) -> dict[str, Any]:
    return {
        "schema": "666.chatbackup.parser-receipt.v1",
        "toolVersion": APP_VERSION,
        "sourceUrl": chat.source_url,
        "shareId": chat.share_id,
        "conversationType": chat.conversation_type,
        "isGroupChat": chat.is_group_chat,
        "groupChatEvidence": list(chat.group_chat_evidence),
        "participantCount": len(chat.participants),
        "parser": chat.parser,
        "parserDetails": chat.parser_details,
        "attempts": _json_safe_clone(chat.parser_attempts),
        "primaryParserError": chat.primary_parser_error or None,
        "sourceHtmlSha256": chat.source_html_sha256 or None,
        "sourceHtmlChars": chat.source_html_chars,
        "sourceCaptureStatus": chat.source_capture_status,
        "integrity": chat.integrity_profile(),
    }

def build_json_export(
    *,
    content: str,
    title: str,
    source_url: str = "",
    source_mode: str = "manual",
    chat: ChatBackup | None = None,
    local_assets: list[dict[str, Any]] | None = None,
    selected_asset_keys: set[str] | None = None,
) -> str:
    return json.dumps(
        build_machine_payload(
            content=content,
            title=title,
            source_url=source_url,
            source_mode=source_mode,
            chat=chat,
            local_assets=local_assets,
            selected_asset_keys=selected_asset_keys,
        ),
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def build_jsonl_export(
    *,
    content: str,
    title: str,
    source_url: str = "",
    source_mode: str = "manual",
    chat: ChatBackup | None = None,
    local_assets: list[dict[str, Any]] | None = None,
    selected_asset_keys: set[str] | None = None,
) -> str:
    payload = build_machine_payload(
        content=content,
        title=title,
        source_url=source_url,
        source_mode=source_mode,
        chat=chat,
        local_assets=local_assets,
        selected_asset_keys=selected_asset_keys,
    )
    meta = {key: value for key, value in payload.items() if key not in {"messages", "renderedContent"}}
    records: list[dict[str, Any]] = [{"recordType": "metadata", **meta}]
    for message in payload.get("messages", []):
        records.append({"recordType": "message", **message})
    records.append(
        {
            "recordType": "renderedContent",
            "content": payload.get("renderedContent", ""),
            "sha256": payload.get("renderedContentSha256", ""),
        }
    )
    return "\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in records) + "\n"


def write_verified(path: str | Path, content: str, encoding: str = "utf-8") -> Path:
    """Schreibt den Export bytegenau und prüft ihn ohne Newline-Normalisierung.

    Textmodus-Readback mit ``newline=None`` normalisiert CRLF/CR zu LF und kann
    deshalb bei längeren Chats mit gemischten Zeilenenden einen falschen
    Integritätsfehler auslösen. Die Verifikation arbeitet bewusst auf Byte-Ebene.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    expected = content.encode(encoding)
    target.write_bytes(expected)
    if not target.exists():
        raise ChatBackupError("Die Datei wurde nach dem Schreiben nicht gefunden.")

    expected_size = len(expected)
    actual_size = target.stat().st_size
    if actual_size != expected_size:
        raise ChatBackupError(
            "Die gespeicherte Datei besitzt nach dem Rücklesen eine abweichende Byte-Länge. "
            f"Erwartet: {expected_size}, gelesen: {actual_size}."
        )

    expected_hash = hashlib.sha256(expected).hexdigest()
    actual_hash = hashlib.sha256()
    with target.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            actual_hash.update(chunk)

    if actual_hash.hexdigest() != expected_hash:
        raise ChatBackupError(
            "Die gespeicherte Datei stimmt nach dem bytegenauen SHA-256-Rücklesen "
            "nicht mit dem Export überein."
        )
    return target


def unique_path(directory: str | Path, base_name: str, extension: str) -> Path:
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    extension = extension if extension.startswith(".") else f".{extension}"
    candidate = folder / f"{base_name}{extension}"
    counter = 2
    while candidate.exists():
        candidate = folder / f"{base_name}_{counter}{extension}"
        counter += 1
    return candidate


def sanitize_heading(value: str) -> str:
    return re.sub(r"\s{2,}", " ", re.sub(r"[\r\n]+", " ", str(value or ""))).strip()


def sanitize_file_name(value: str) -> str:
    name = str(value or "ChatGPT_Gespraech")
    name = re.sub(r"[\\/:*?\"<>|]", "-", name)
    name = re.sub(r"[\r\n\t]+", " ", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)
    name = re.sub(r"^[-_. ]+|[-_. ]+$", "", name)[:80]
    return name or "ChatGPT_Gespraech"


def escape_markdown_label(value: str) -> str:
    return re.sub(r"[\[\]]", lambda match: "\\" + match.group(0), str(value or ""))


def extract_share_id(url: str) -> str:
    match = re.search(r"/(?:share|s)/([^/?#]+)", str(url or ""), re.IGNORECASE)
    return match.group(1) if match else ""


def author_name_for_role(role: str) -> str:
    if role == "user":
        return "Benutzer"
    if role == "tool":
        return "Tool"
    return "ChatGPT"


def has_unclosed_code_fence(text: str) -> bool:
    return len(re.findall(r"```", str(text or ""))) % 2 != 0


def format_local_datetime(value: datetime) -> str:
    return value.astimezone().strftime("%d.%m.%Y, %H:%M:%S")


def format_unix_timestamp(timestamp: float) -> str:
    seconds = timestamp / 1000 if timestamp > 100_000_000_000 else timestamp
    return format_local_datetime(datetime.fromtimestamp(seconds).astimezone())


def file_date_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class _StaticMessageParser(HTMLParser):
    _SSR_BODY_ATTRS = {
        "user": {"data-user-message-copy", "data-submit-message-animation-target"},
        "assistant": {"data-assistant-markdown-root", "data-assistant-markdown"},
    }

    def __init__(self, *, ssr: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active_depth: int | None = None
        self.active_role: str | None = None
        self.active_chunks: list[str] = []
        self.messages: list[tuple[str, str, str, list[ChatAsset]]] = []
        self.ssr = ssr
        self.transcript_depth: int | None = None
        self.body_depth: int | None = None
        self.body_chunks: list[str] | None = None
        self.ignored_depth: int | None = None
        self.active_id = ""
        self.assets: dict[str, ChatAsset] = {}
        self.title = ""
        self._in_title = False

    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        attrs_dict = {key: value or "" for key, value in attrs}

        if tag_lower in self._VOID_TAGS:
            if self.active_depth is not None and tag_lower in {"br", "hr"}:
                self._append_text("\n")
            if self.ssr and self.active_depth is not None and self.ignored_depth is None and tag_lower == "img":
                url = (attrs_dict.get("data-src") or attrs_dict.get("src", "")).strip()
                if re.match(r"^https?://[^/\s?#]+", url, re.IGNORECASE) and url not in self.assets:
                    name = attrs_dict.get("alt") or f"Chat image {len(self.assets) + 1}"
                    self.assets[url] = ChatAsset("image", name, url=url, source="ssr-html")
            return

        self.depth += 1
        if tag_lower == "title":
            self._in_title = True
        if self.ssr and tag_lower in {"script", "style", "template"} and self.ignored_depth is None:
            self.ignored_depth = self.depth
        if self.ignored_depth is not None:
            return
        if self.ssr and self.transcript_depth is None and "data-conversation-transcript" in attrs_dict:
            self.transcript_depth = self.depth
        if self.active_depth is None:
            role_attr = "data-message-role" if self.ssr else "data-message-author-role"
            role = attrs_dict.get(role_attr, "")
            if role in {"user", "assistant"} and (not self.ssr or self.transcript_depth is not None):
                self.active_depth = self.depth
                self.active_role = role
                self.active_id = attrs_dict.get("id", "") if self.ssr else ""
                self.active_chunks = []
                self.body_chunks = None
                self.assets = {}
        if self.active_role is not None and self.ssr and self.body_chunks is None:
            if self._SSR_BODY_ATTRS[self.active_role].intersection(attrs_dict):
                self.body_depth = self.depth
                self.body_chunks = []
        if self.active_depth is not None and self.active_depth != self.depth:
            if tag_lower in {"p", "div", "article", "li", "pre", "h1", "h2", "h3"}:
                self._append_text("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self._VOID_TAGS:
            self.handle_starttag(tag, attrs)
        elif self.ssr:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower in self._VOID_TAGS:
            return
        if tag_lower == "title":
            self._in_title = False
        if self.body_depth == self.depth:
            self.body_depth = None
        if self.ignored_depth == self.depth:
            self.ignored_depth = None
        if self.active_depth == self.depth and self.active_role:
            chunks = self.body_chunks if self.body_chunks is not None else self.active_chunks
            text = clean_export_text("".join(chunks))
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if text or self.assets:
                self.messages.append((self.active_role, text, self.active_id, list(self.assets.values())))
            self.active_depth = None
            self.active_role = None
            self.active_chunks = []
        if self.transcript_depth == self.depth:
            self.transcript_depth = None
        self.depth = max(0, self.depth - 1)

    def _append_text(self, data: str) -> None:
        if self.ignored_depth is not None:
            return
        self.active_chunks.append(data)
        if self.body_depth is not None and self.body_chunks is not None:
            self.body_chunks.append(data)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self.active_depth is not None:
            self._append_text(data)


def extract_static_dom_conversation(page_html: str, source_url: str, *, ssr: bool = False) -> ChatBackup:
    parser = _StaticMessageParser(ssr=ssr)
    parser.feed(page_html)
    seen: set[tuple[str, str]] = set()
    messages: list[ChatMessage] = []
    for role, text, message_id, assets in parser.messages:
        if not ssr:
            key = (role, text)
            if key in seen:
                continue
            seen.add(key)
        messages.append(ChatMessage(
            role=role, author=author_name_for_role(role), text=text, message_id=message_id, assets=assets,
            content_type="ssr-html" if ssr else "",
            participant_id="chatgpt" if role == "assistant" else "",
            participant_display_name=author_name_for_role(role),
            participant_kind="assistant" if role == "assistant" else "human",
            participant_resolution="ROLE_EXPLICIT" if role == "assistant" else "UNRESOLVED",
        ))
    title = re.sub(r"^ChatGPT\s*[-–—:]\s*", "", parser.title, flags=re.IGNORECASE).strip()
    stats = ExportStats(source_entries=len(messages), exported=len(messages))
    return ChatBackup(
        title=title or "ChatGPT Gespräch",
        source_url=source_url,
        share_id=extract_share_id(source_url) or "shared",
        messages=messages,
        stats=stats,
        parser="ssr-dom-transcript" if ssr else "static-dom-fallback",
        parser_details="HTML-SSR: data-conversation-transcript / data-message-role" if ssr else "Statisch gerenderte sichtbare Nachrichten",
    )
