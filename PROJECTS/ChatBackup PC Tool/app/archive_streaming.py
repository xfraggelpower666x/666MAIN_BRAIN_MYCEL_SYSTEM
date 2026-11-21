"""Bounded incremental conversations.json array reader for offline ZIP batch imports.

Only one JSON conversation object is kept in the parse buffer at a time.
No archive extraction, network access or implicit filesystem writes.
"""
from __future__ import annotations

import codecs
import json
import zipfile
from pathlib import Path
from typing import Callable, Iterator

from archive_intelligence import ArchiveImportError, MAX_CONVERSATIONS, MAX_MEMBER_BYTES, inspect_export, parse_conversation

CHUNK_BYTES = 65536
MAX_OBJECT_CHARS = 24 * 1024 * 1024


class StreamingCancelled(ArchiveImportError):
    """Cancellation requested at a safe parsing boundary."""


def iter_export_conversations(
    path: str | Path,
    *,
    stop: Callable[[], bool] | None = None,
    progress: Callable[[dict], None] | None = None,
) -> Iterator:
    """Yield bounded parsed conversations from a validated ZIP.

    A malformed or unsupported entry fails the entire ZIP. The batch caller is
    responsible for rolling back the current ZIP transaction and not checkpointing.
    """
    report = inspect_export(path)
    if report["status"] != "SUPPORTED_JSON":
        raise ArchiveImportError("Exactly one conversations.json required")
    with zipfile.ZipFile(path) as zf:
        info = zf.getinfo(report["candidates"][0])
        if info.file_size > MAX_MEMBER_BYTES:
            raise ArchiveImportError("JSON member size exceeds policy")
        decoder = codecs.getincrementaldecoder("utf-8-sig")("strict")
        parser = json.JSONDecoder()
        with zf.open(info, "r") as stream:
            text = ""
            cursor = 0
            total_read = 0
            eof = False
            initialized = False
            after_value = False
            seen = 0
            finished = False

            def read_more() -> bool:
                nonlocal text, cursor, total_read, eof
                if stop is not None and stop():
                    raise StreamingCancelled("Stopped while streaming conversation JSON")
                raw = stream.read(CHUNK_BYTES)
                total_read += len(raw)
                if total_read > MAX_MEMBER_BYTES:
                    raise ArchiveImportError("JSON bytes exceed policy")
                if not raw:
                    text += decoder.decode(b"", final=True)
                    eof = True
                    return False
                text += decoder.decode(raw, final=False)
                if len(text) - cursor > MAX_OBJECT_CHARS:
                    raise ArchiveImportError("One JSON conversation exceeds object memory budget")
                if progress is not None:
                    progress({"stage": "STREAMING", "json_bytes": total_read,
                              "json_total": info.file_size,
                              "json_percent": round(100 * total_read / max(1, info.file_size), 2),
                              "conversations": seen})
                return True

            while True:
                if stop is not None and stop():
                    raise StreamingCancelled("Stopped during conversation parsing")
                # Discard consumed prefixes regularly to bound retained text.
                if cursor > CHUNK_BYTES:
                    text = text[cursor:]
                    cursor = 0
                while cursor >= len(text):
                    if eof:
                        break
                    read_more()
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
                    if cursor >= len(text) and not eof:
                        read_more()
                if cursor >= len(text) and eof:
                    break
                if not initialized:
                    if text[cursor] != "[":
                        raise ArchiveImportError("conversations.json must be an array")
                    initialized = True
                    cursor += 1
                    continue
                if finished:
                    if cursor < len(text) and not text[cursor].isspace():
                        raise ArchiveImportError("Unexpected data after conversations array")
                    if eof:
                        break
                    read_more()
                    continue
                marker = text[cursor]
                if marker == "]":
                    if after_value:
                        raise ArchiveImportError("Trailing comma in conversation array")
                    finished = True
                    cursor += 1
                    continue
                if after_value:
                    if marker != ",":
                        raise ArchiveImportError("Expected separator between conversations")
                    after_value = False
                    cursor += 1
                    continue
                if marker != "{":
                    raise ArchiveImportError("Conversation entry must be an object")
                while True:
                    try:
                        value, consumed = parser.raw_decode(text, cursor)
                        break
                    except json.JSONDecodeError as exc:
                        if eof:
                            raise ArchiveImportError("Malformed conversation JSON") from exc
                        if len(text) - cursor > MAX_OBJECT_CHARS:
                            raise ArchiveImportError("Conversation entry exceeds memory budget")
                        read_more()
                seen += 1
                if seen > MAX_CONVERSATIONS:
                    raise ArchiveImportError("Too many conversations")
                yield parse_conversation(value, report["candidates"][0])
                cursor = consumed
                # Empty input after value is handled on next read.
                while cursor >= len(text) and not eof:
                    read_more()
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
                    if cursor >= len(text) and not eof:
                        read_more()
                if cursor < len(text) and text[cursor] == ",":
                    cursor += 1
                    after_value = False
                    # Reaching a closing bracket from here must fail.
                    while cursor >= len(text) and not eof:
                        read_more()
                    while cursor < len(text) and text[cursor].isspace():
                        cursor += 1
                        if cursor >= len(text) and not eof:
                            read_more()
                    if cursor < len(text) and text[cursor] == "]":
                        raise ArchiveImportError("Trailing comma")
                elif cursor < len(text) and text[cursor] == "]":
                    finished = True
                    cursor += 1
                else:
                    if eof:
                        raise ArchiveImportError("Unterminated conversation array")
                    # Need separator in the next chunk.
                    after_value = True
            if not initialized or not finished:
                raise ArchiveImportError("Unterminated conversation array")
