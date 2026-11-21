"""R5.5 additive message navigation; works with existing conversation_view dictionaries."""
from __future__ import annotations

from typing import Any


def message_position(conversation: dict[str, Any], message_id: str | None = None) -> int:
    """Resolve an exact message ID, never a shortened snippet or fuzzy match."""
    messages = conversation.get('messages', [])
    if not isinstance(messages, list):
        raise ValueError('Invalid conversation messages')
    if not messages:
        return -1
    if message_id is None:
        return 0
    for index, message in enumerate(messages):
        if message.get('id') == message_id:
            return index
    raise ValueError('Selected message ID not found in conversation')


def message_context(conversation: dict[str, Any], index: int, *, radius: int = 2,
                    highlight: str = '') -> dict[str, Any]:
    """Read-only context window with stable original index and match spans.

    The indexed conversation is authoritative. Search snippets must never replace
    full message text. Parent IDs are displayed as provenance, not branch order.
    """
    messages = conversation.get('messages', [])
    if not isinstance(messages, list) or not messages:
        raise ValueError('Conversation contains no indexed messages')
    if not isinstance(index, int) or index < 0 or index >= len(messages):
        raise ValueError('Message position out of bounds')
    if not isinstance(radius, int) or radius < 0 or radius > 20:
        raise ValueError('Context radius out of bounds')
    if not isinstance(highlight, str) or len(highlight) > 500:
        raise ValueError('Highlight term too long')
    selected = messages[index]
    start = max(0, index - radius)
    end = min(len(messages), index + radius + 1)
    segments = []
    for pos in range(start, end):
        message = messages[pos]
        body = message.get('text', '')
        if not isinstance(body, str):
            body = str(body)
        spans = []
        if pos == index and highlight:
            folded = body.casefold()
            needle = highlight.casefold()
            # Casefold may change character counts (e.g. ß -> ss), so use
            # original-length literal matching and never synthesize offsets.
            from re import finditer, escape, IGNORECASE
            spans = [(m.start(), m.end()) for m in finditer(escape(highlight), body, IGNORECASE)]
        segments.append({
            'position': pos, 'id': message.get('id'), 'role': message.get('role'),
            'parent': message.get('parent'), 'text': body,
            'selected': pos == index, 'highlight_spans': spans
        })
    return {
        'conversation_id': conversation.get('id'),
        'title': conversation.get('title'),
        'index': index, 'count': len(messages),
        'has_previous': index > 0, 'has_next': index < len(messages) - 1,
        'context': segments,
        'visual_parity': 'NOT_CLAIMED',
    }
