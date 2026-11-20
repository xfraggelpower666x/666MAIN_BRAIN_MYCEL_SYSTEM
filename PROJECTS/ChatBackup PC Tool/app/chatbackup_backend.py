from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chatbackup_core import (
    ChatBackup,
    AuthWallDetected,
    build_machine_payload,
    build_parser_receipt,
    build_raw_source_bundle,
    build_structure_inspector_payload,
    analyze_manual_transcript,
    enrich_chat_image_urls_from_html,
    fetch_share_page,
    normalize_and_validate_share_url,
    parse_shared_conversation,
    reparse_share_source,
)


@dataclass(slots=True)
class BackendConfig:
    """Runtime policy for the loss-aware ChatBackup backend."""

    request_timeout_seconds: int = 60
    download_retries: int = 3
    preserve_raw_source: bool = True
    max_raw_html_chars: int = 12_000_000


class ChatBackend:
    """Single orchestration boundary for ChatGPT share capture and re-analysis.

    The backend deliberately separates transport, parser, normalized rendered text,
    raw message source, UI/copy-field extraction, asset metadata and archival output.
    It never executes JavaScript extracted from a conversation.
    """

    BACKEND_ID = "666.chatbackup.backend.v1"
    BACKEND_VERSION = "1.4.0"

    def __init__(self, config: BackendConfig | None = None) -> None:
        self.config = config or BackendConfig()

    def load(self, raw_url: str) -> ChatBackup:
        url = normalize_and_validate_share_url(raw_url)
        page = fetch_share_page(
            url,
            timeout_seconds=self.config.request_timeout_seconds,
            retries=self.config.download_retries,
        )
        return self.parse_html(page, url)

    def parse_html(self, page_html: str, source_url: str) -> ChatBackup:
        url = normalize_and_validate_share_url(source_url)
        chat = parse_shared_conversation(page_html, url)
        enrich_chat_image_urls_from_html(chat, page_html)
        chat.source_html_chars = len(page_html)

        import hashlib

        chat.source_html_sha256 = hashlib.sha256(
            page_html.encode("utf-8", errors="replace")
        ).hexdigest()
        if self.config.preserve_raw_source and len(page_html) <= max(1, self.config.max_raw_html_chars):
            chat.source_html = page_html
            chat.source_capture_status = "RAW_PRESERVED"
        elif self.config.preserve_raw_source:
            chat.source_capture_status = "RAW_TOO_LARGE_NOT_STORED"
            warning = (
                f"Share-HTML ({len(page_html)} Zeichen) überschreitet das Raw-Capture-Limit "
                f"von {self.config.max_raw_html_chars}."
            )
            if warning not in chat.warnings:
                chat.warnings.append(warning)
        else:
            chat.source_capture_status = "RAW_CAPTURE_DISABLED"
        return chat

    def analyze_manual_text(self, text: str, *, title: str = "Manual Chat Import") -> ChatBackup:
        """Recover a structured conversation from text manually copied from ChatGPT."""
        return analyze_manual_transcript(text, title=title)

    def recover_browser_transcript(
        self,
        text: str,
        *,
        source_url: str,
        title: str = "Browser-Assisted Chat Recovery",
    ) -> ChatBackup:
        """Reconstruct a chat copied from an authenticated browser session.

        This does not access browser cookies, inject code, or bypass authentication. The user
        opens ChatGPT normally, copies the visible conversation, and the existing fail-closed
        transcript analyzer reconstructs only identities/turns explicitly supported by text.
        """
        chat = analyze_manual_transcript(text, title=title)
        chat.source_url = source_url
        chat.parser = "browser-assisted-transcript"
        chat.parser_details = "Authenticated browser clipboard recovery / fail-closed transcript analysis"
        chat.source_capture_status = "BROWSER_CLIPBOARD_RECOVERY"
        chat.warnings.insert(0,
            "Browser-assisted recovery used because the direct Share response did not provide conversation payload. "
            "Clipboard recovery preserves text structure but cannot recreate image/file bytes that were not copied."
        )
        chat.parser_attempts.insert(0, {
            "parser": "direct-share-probe",
            "status": "AUTH_WALL_DETECTED",
        })
        return chat

    def reparse(self, page_html: str, source_url: str) -> ChatBackup:
        """Run the current parser generation against a previously archived HTML source."""
        chat = reparse_share_source(page_html, source_url)
        if not self.config.preserve_raw_source:
            chat.source_html = ""
            chat.source_capture_status = "RAW_CAPTURE_DISABLED_AFTER_REPARSE"
        return chat

    def machine_payload(
        self,
        *,
        content: str,
        title: str,
        source_url: str = "",
        source_mode: str = "manual",
        chat: ChatBackup | None = None,
        local_assets: list[dict[str, Any]] | None = None,
        selected_asset_keys: set[str] | None = None,
    ) -> dict[str, Any]:
        return build_machine_payload(
            content=content,
            title=title,
            source_url=source_url,
            source_mode=source_mode,
            chat=chat,
            local_assets=local_assets,
            selected_asset_keys=selected_asset_keys,
        )

    @staticmethod
    def raw_source_bundle(chat: ChatBackup) -> dict[str, Any]:
        return build_raw_source_bundle(chat)

    @staticmethod
    def parser_receipt(chat: ChatBackup) -> dict[str, Any]:
        return build_parser_receipt(chat)

    @staticmethod
    def structure_inspector_payload(chat: ChatBackup) -> dict[str, Any]:
        return build_structure_inspector_payload(chat)

    @classmethod
    def identity(cls) -> dict[str, str]:
        return {
            "backendId": cls.BACKEND_ID,
            "backendVersion": cls.BACKEND_VERSION,
        }
