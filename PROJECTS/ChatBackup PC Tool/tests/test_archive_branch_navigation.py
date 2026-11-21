"""Parent-child branch navigation on stored message IDs (no inferred edges)."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from archive_message_navigation import branch_index, branch_context, message_position
from archive_intelligence import ArchiveCatalog, ArchiveConversation, ArchiveMessage
from archive_extensions import conversation_view


def conversation():
    return {'id':'branch-chat','messages':[
        {'id':'root','parent':None,'text':'start'},
        {'id':'answer-a','parent':'root','text':'branch a'},
        {'id':'answer-b','parent':'root','text':'branch b'},
        {'id':'a-leaf','parent':'answer-a','text':'leaf a'},
        {'id':'b-leaf','parent':'answer-b','text':'leaf b'},
        {'id':'unresolved','parent':'absent','text':'disconnected'}]}


def test_direct_children_siblings_parent_and_lineage():
    data=conversation()
    g=branch_index(data)
    assert branch_context(data,0,graph=g)['children']==[1,2]
    a=branch_context(data,1,graph=g)
    assert a['parent']==0
    assert a['siblings']==[2]
    assert a['children']==[3]
    assert a['lineage']==[0,1]
    assert branch_context(data,4,graph=g)['lineage']==[0,2,4]
    assert branch_context(data,5,graph=g)['warnings']==['PARENT_UNRESOLVED']
    assert branch_context(data,5,graph=g)['parent'] is None


def test_branch_index_rejects_duplicate_ids():
    data=conversation()
    data['messages'][1]['id']='root'
    with pytest.raises(ValueError,match='duplicate'):
        branch_index(data)


def test_self_parent_and_cycle_do_not_invent_trusted_lineage():
    data={'messages':[
        {'id':'one','parent':'two'},
        {'id':'two','parent':'one'},
        {'id':'alone','parent':'alone'}]}
    graph=branch_index(data)
    assert set(graph['cyclic'])=={0,1}
    assert 'PARENT_CYCLE' in branch_context(data,0,graph=graph)['warnings']
    assert 'CYCLE_MEMBER' in branch_context(data,1,graph=graph)['warnings']
    self_ref=branch_context(data,2,graph=graph)
    assert self_ref['parent'] is None
    assert 'PARENT_UNRESOLVED' in self_ref['warnings']


def test_sqlite_parent_id_roundtrip_with_real_branch(tmp_path):
    chat=ArchiveConversation('conversation','Branches',[
        ArchiveMessage('root','user','start',created_at=1),
        ArchiveMessage('a','assistant','A',parent_id='root',created_at=2),
        ArchiveMessage('b','assistant','B',parent_id='root',created_at=3),
        ArchiveMessage('branch-leaf','user','followup B',parent_id='b',created_at=4)],
        'conversations.json',4)
    with ArchiveCatalog(tmp_path/'branch.sqlite') as db:
        db.add([chat],'sha','test.zip')
        stored=conversation_view(db,'conversation')
    pos=message_position(stored,'b')
    g=branch_index(stored)
    assert branch_context(stored,pos,graph=g)['siblings']==[1]
    assert branch_context(stored,3,graph=g)['lineage']==[0,2,3]


def test_gui_has_branch_controls_without_creating_window():
    spec=importlib.util.spec_from_file_location(
        'chatbackup_branch_gui',ROOT/'tools'/'archive_intelligence_gui.py')
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.branch_index is branch_index
    assert mod.branch_context is branch_context
    names=mod.ArchiveWindow.view_conversation.__code__.co_names
    assert 'branch_index' in names
