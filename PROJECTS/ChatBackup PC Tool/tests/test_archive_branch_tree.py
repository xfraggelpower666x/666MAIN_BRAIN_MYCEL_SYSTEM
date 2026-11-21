"""R5.5 branch-tree regression: roots, paging contract, cycles and identity."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
sys.path.insert(0,str(ROOT/'tools'))
from archive_message_navigation import branch_index
from archive_branch_tree import project_branch_tree,tree_ancestry,describe_tree_node


def sample():
    return {'id':'chat','messages':[
        {'id':'root','parent':None,'role':'user','text':'start'},
        {'id':'child-a','parent':'root','role':'assistant','text':'answer A'},
        {'id':'child-b','parent':'root','role':'assistant','text':'answer B'},
        {'id':'grandchild','parent':'child-b','role':'user','text':'followup'},
        {'id':'missing','parent':'not-in-index','role':'assistant','text':'incomplete'}]}


def test_branch_forest_and_exact_selected_path():
    chat=sample()
    projection=project_branch_tree(chat)
    assert projection['status']=='PARTIAL'
    assert projection['roots']==[0,4]
    assert projection['children'][0]==[1,2]
    assert projection['children'][2]==[3]
    assert tree_ancestry(projection,3)==[0,2,3]
    node=describe_tree_node(chat,projection,4)
    assert node['id']=='missing'
    assert node['warnings']==['MISSING_PARENT']
    assert projection['source']=='INDEXED_PARENT_ID_ONLY'


def test_cycle_nodes_visible_once_with_warning():
    chat={'messages':[
        {'id':'one','parent':'two','text':'a'},
        {'id':'two','parent':'one','text':'b'},
        {'id':'descendant','parent':'two','text':'c'}]}
    tree=project_branch_tree(chat)
    assert tree['roots']==[0,1]
    assert tree['children'][1]==[2]
    assert 'CYCLE_EDGE_OMITTED_FROM_TREE' in tree['warnings'][0]
    assert tree_ancestry(tree,2)==[1,2]
    positions=tree['roots']+tree['children'][1]
    assert sorted(positions)==[0,1,2]


def test_tree_rejects_invalid_position_and_duplicates():
    projection=project_branch_tree(sample())
    for pos in (-1,100):
        with pytest.raises(ValueError):
            tree_ancestry(projection,pos)
    chat=sample()
    chat['messages'][1]['id']='root'
    with pytest.raises(ValueError,match='duplicate'):
        project_branch_tree(chat)


def test_thousands_of_nodes_iterative_no_recursion_limit():
    count=2500
    chat={'messages':[{'id':f'm{i}','parent':f'm{i-1}' if i else None,'text':'hello'}
                      for i in range(count)]}
    tree=project_branch_tree(chat)
    assert tree['status']=='VERIFIED'
    assert tree['roots']==[0]
    assert tree_ancestry(tree,count-1)==list(range(count))


def test_tree_labels_bounded_and_source_unchanged():
    chat=sample()
    before=repr(chat)
    projection=project_branch_tree(chat)
    info=describe_tree_node(chat,projection,0,max_preview=16)
    assert len(info['preview'])<=16
    assert projection['originals_modified'] is False
    assert repr(chat)==before


def test_tree_window_module_imports_without_graphics_display():
    modpath=ROOT/'tools'/'archive_branch_tree_ui.py'
    spec=importlib.util.spec_from_file_location('chatbackup_tree_ui_r55',modpath)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.open_branch_tree_window)
    assert module.PAGE <= 150
    gui_path=ROOT/'tools'/'archive_intelligence_gui.py'
    gui_spec=importlib.util.spec_from_file_location('chatbackup_tree_gui_r55',gui_path)
    assert gui_spec and gui_spec.loader
    gui=importlib.util.module_from_spec(gui_spec)
    gui_spec.loader.exec_module(gui)
    assert gui.open_branch_tree_window.__name__ == module.open_branch_tree_window.__name__
