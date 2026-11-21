"""R5.5 read-only branch-tree projection for existing indexed chat messages.

Every displayed message comes from an indexed identity. Broken and cyclic
parent edges remain visible as warnings rather than being presented as facts.
No database or original archive writes.
"""
from __future__ import annotations

from typing import Any
from archive_message_navigation import branch_index

MAX_TREE_MESSAGES = 250000


def project_branch_tree(conversation: dict[str, Any], *,
                        graph: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a cycle-safe, deterministic forest of every indexed message."""
    messages = conversation.get('messages', [])
    if not isinstance(messages, list) or len(messages) > MAX_TREE_MESSAGES:
        raise ValueError('Invalid or oversized indexed conversation')
    graph = branch_index(conversation) if graph is None else graph
    if len(graph['parents']) != len(messages):
        raise ValueError('Branch index does not match conversation')
    # Cutting only visualization links is not a repair of the stored relation.
    # Cycle members become separate diagnostic roots, with warning markers.
    cyclic = set(graph['cyclic'])
    parents = [None if i in cyclic else parent
               for i, parent in enumerate(graph['parents'])]
    children: list[list[int]] = [[] for _ in messages]
    roots = []
    for pos, parent in enumerate(parents):
        if parent is None:
            roots.append(pos)
        else:
            children[parent].append(pos)
    warning_map: dict[int, list[str]] = {}
    for row in graph['unresolved']:
        warning_map.setdefault(row['position'], []).append(row.get('reason', 'PARENT_UNRESOLVED'))
    for pos in cyclic:
        warning_map.setdefault(pos, []).append('CYCLE_EDGE_OMITTED_FROM_TREE')
    # Ancestors of a cycle are still reachable as children of the diagnostic root.
    # Strict identity and deterministic original indexed ordering.
    return {'schema': '666.chatbackup.branch-tree.v1',
            'count': len(messages),
            'roots': roots,
            'parents': parents,
            'children': children,
            'warnings': warning_map,
            'status': 'PARTIAL' if warning_map else 'VERIFIED',
            'source': 'INDEXED_PARENT_ID_ONLY', 'originals_modified': False}


def tree_ancestry(projection: dict[str, Any], position: int) -> list[int]:
    """Find an exact message path from a visual root (non-recursive)."""
    count = projection['count']
    if not isinstance(position, int) or not 0 <= position < count:
        raise ValueError('Invalid message position')
    route = []
    seen = set()
    cursor = position
    while cursor is not None:
        if cursor in seen:
            raise ValueError('Unexpected cycle in visual tree projection')
        seen.add(cursor)
        route.append(cursor)
        cursor = projection['parents'][cursor]
    return route[::-1]


def describe_tree_node(conversation: dict[str, Any], projection: dict[str, Any],
                       position: int, *, max_preview: int = 100) -> dict[str, Any]:
    """Small bounded user-facing label, original IDs preserved separately."""
    if not 16 <= max_preview <= 240:
        raise ValueError('Invalid preview bound')
    message = conversation['messages'][position]
    body = message.get('text', '')
    preview = (' '.join(body.split()) if isinstance(body, str) else '')[:max_preview]
    warnings = projection['warnings'].get(position, [])
    return {'position': position, 'id': message['id'],
            'role': message.get('role', 'unknown'),
            'preview': preview,
            'children': len(projection['children'][position]),
            'warnings': list(warnings)}
