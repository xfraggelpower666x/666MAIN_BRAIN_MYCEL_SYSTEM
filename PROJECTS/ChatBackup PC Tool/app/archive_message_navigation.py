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
            # Use regex-provided offsets in the original text; avoid index
            # distortion from casefold expansions (e.g. ß -> ss).
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

def branch_index(conversation: dict[str, Any]) -> dict[str, Any]:
    """Index only existing parent IDs; report unresolved edges and cycles."""
    messages = conversation.get('messages', [])
    if not isinstance(messages, list):
        raise ValueError('Invalid conversation messages')
    ids = {}
    for pos, msg in enumerate(messages):
        identity = msg.get('id') if isinstance(msg, dict) else None
        if not isinstance(identity, str) or not identity or identity in ids:
            raise ValueError('Invalid or duplicate indexed message ID')
        ids[identity] = pos
    parents = []
    children = [[] for _ in messages]
    unresolved = []
    for pos, msg in enumerate(messages):
        pid = msg.get('parent')
        if pid is None or pid == '':
            parents.append(None)
        elif not isinstance(pid, str) or pid not in ids or ids[pid] == pos:
            parents.append(None)
            unresolved.append({'position': pos, 'message_id': msg['id'],
                               'parent_id': str(pid), 'reason': 'SELF_PARENT' if pid == msg['id'] else 'MISSING_PARENT'})
        else:
            parent = ids[pid]
            parents.append(parent)
            children[parent].append(pos)
    cyclic = set()
    for pos in range(len(messages)):
        seen = {}
        path = []
        cursor = pos
        while cursor is not None and cursor not in seen:
            seen[cursor] = len(path)
            path.append(cursor)
            cursor = parents[cursor]
        if cursor is not None:
            cyclic.update(path[seen[cursor]:])
    return {'ids': ids, 'parents': parents, 'children': children,
            'unresolved': unresolved, 'cyclic': cyclic}


def branch_context(conversation: dict[str, Any], index: int,
                   *, graph: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read-only relationships and ancestor route for the selected message."""
    messages = conversation.get('messages', [])
    if not isinstance(messages, list) or not isinstance(index, int) or not 0 <= index < len(messages):
        raise ValueError('Invalid branch position')
    graph = branch_index(conversation) if graph is None else graph
    parents, children = graph['parents'], graph['children']
    parent = parents[index]
    siblings = [pos for pos in children[parent] if pos != index] if parent is not None else []
    lineage = []
    visited = set()
    cursor = index
    cycle = False
    while cursor is not None:
        if cursor in visited:
            cycle = True
            break
        visited.add(cursor)
        lineage.append(cursor)
        cursor = parents[cursor]
    lineage.reverse()
    warnings = []
    if any(row['position'] == index for row in graph['unresolved']):
        warnings.append('PARENT_UNRESOLVED')
    if cycle:
        warnings.append('PARENT_CYCLE')
    if index in graph['cyclic']:
        warnings.append('CYCLE_MEMBER')
    return {'position': index, 'id': messages[index]['id'],
            'parent': parent, 'children': list(children[index]), 'siblings': siblings,
            'lineage': lineage, 'warnings': warnings,
            'parent_id_recorded': messages[index].get('parent'),
            'source': 'INDEXED_PARENT_ID_ONLY', 'visual_parity': 'NOT_CLAIMED'}
