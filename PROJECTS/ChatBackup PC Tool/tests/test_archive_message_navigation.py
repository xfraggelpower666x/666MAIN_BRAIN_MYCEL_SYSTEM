"""R5.5 regression: exact search-hit navigation and local message context."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from archive_message_navigation import message_position, message_context
from archive_intelligence import ArchiveCatalog, ArchiveConversation, ArchiveMessage
from archive_navigation import search_filtered
from archive_extensions import conversation_view


def sample():
    return {'id': 'chat', 'title': 'Cyber', 'messages': [
        {'id': f'm-{i}', 'role': 'user' if i % 2 == 0 else 'assistant',
         'text': f'before {i} DARK techno and after', 'parent': f'm-{i-1}' if i else None}
        for i in range(6)]}


def test_exact_message_id_and_context_boundaries():
    data = sample()
    assert message_position(data, 'm-3') == 3
    center = message_context(data, 3, radius=2, highlight='dark')
    assert center['index'] == 3 and center['count'] == 6
    assert [row['position'] for row in center['context']] == [1, 2, 3, 4, 5]
    assert [row['id'] for row in center['context'] if row['selected']] == ['m-3']
    assert len(center['context'][2]['highlight_spans']) == 1
    assert center['context'][2]['text'][slice(*center['context'][2]['highlight_spans'][0])] == 'DARK'
    assert not center['context'][0]['highlight_spans']
    first = message_context(data, 0)
    assert first['has_previous'] is False and first['has_next'] is True
    last = message_context(data, 5)
    assert last['has_next'] is False and last['has_previous'] is True


def test_missing_message_fails_closed():
    with pytest.raises(ValueError, match='not found'):
        message_position(sample(), 'wrong-id')
    assert message_position({'messages': []}) == -1
    with pytest.raises(ValueError):
        message_context(sample(), -1)


def test_context_highlight_is_literal_not_regex():
    data = sample()
    data['messages'][2]['text'] = 'a.b a*b [a.b]'
    row = message_context(data, 2, radius=0, highlight='a.b')['context'][0]
    assert row['highlight_spans'] == [(0, 3), (9, 12)]


def test_search_id_roundtrip_to_original_indexed_message(tmp_path):
    db_path = tmp_path / 'catalog.sqlite3'
    chat = ArchiveConversation('c-1', 'Sound design', [
        ArchiveMessage('m-1', 'user', 'first idea', created_at=10),
        ArchiveMessage('m-2', 'assistant', 'Deep Dark Techno', created_at=20),
        ArchiveMessage('m-3', 'user', 'closing', created_at=30),
    ], 'export.zip', 30)
    with ArchiveCatalog(db_path) as catalog:
        catalog.add([chat], 'sha', 'export.zip')
        hits = search_filtered(catalog, 'Dark', limit=30)
        assert len(hits) == 1 and hits[0]['message_id'] == 'm-2'
        full = conversation_view(catalog, hits[0]['conversation_id'])
        assert full is not None
        ix = message_position(full, hits[0]['message_id'])
        context = message_context(full, ix, highlight='Dark')
    assert context['index'] == 1
    assert context['context'][1]['id'] == 'm-2'
    assert context['context'][1]['highlight_spans']
    assert context['visual_parity'] == 'NOT_CLAIMED'


def test_gui_navigation_entrypoint_import_without_display():
    path = ROOT / 'tools' / 'archive_intelligence_gui.py'
    spec = importlib.util.spec_from_file_location('archive_gui_nav_r55', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod.ArchiveWindow, 'open_selected_hit')
    assert hasattr(mod.ArchiveWindow, 'view_conversation')
    assert mod.message_position is message_position
    assert mod.message_context is message_context
