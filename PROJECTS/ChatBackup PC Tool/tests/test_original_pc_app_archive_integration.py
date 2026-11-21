"""Vertrag: 666 ChatBackup v1.10.5 bleibt der eigentliche App-Einstieg."""
from __future__ import annotations
import ast
import importlib.util
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'app'/'chatbackup_gui.pyw'
SPEC=ROOT/'666_CHATBACKUP_PC_TOOL.spec'
ARCHIVE=ROOT/'tools'/'archive_intelligence_gui.py'


def test_original_main_application_identity_and_archive_entry():
    text=MAIN.read_text(encoding='utf-8')
    tree=ast.parse(text)
    classes={item.name:item for item in tree.body if isinstance(item,ast.ClassDef)}
    assert 'ChatBackupApp' in classes
    methods={m.name:m for m in classes['ChatBackupApp'].body if isinstance(m,ast.FunctionDef)}
    assert 'open_archive_intelligence' in methods
    launcher=ast.get_source_segment(text,methods['open_archive_intelligence'])
    assert 'ArchiveWindow(master=self)' in launcher
    assert 'ARCHIVE_INTELLIGENCE_IN_PROCESS_WINDOW' in launcher
    assert '666_CHATBACKUP_ARCHIVE_INTELLIGENCE.exe' in launcher  # Legacy-Fallback erhalten
    assert '666 ChatBackup PC Tool v' in text


def test_original_pyinstaller_target_and_tools_import_path():
    text=SPEC.read_text(encoding='utf-8')
    assert 'chatbackup_gui.pyw' in text
    assert 'name="666_CHATBACKUP_PC_TOOL"' in text
    assert 'str(tools_dir)' in text
    assert 'archive_intelligence_gui.py' not in text  # Keine Umstellung des Startskripts


def test_optional_archive_window_is_toplevel_and_has_real_tree_search():
    sys.path.insert(0,str(ROOT/'app'))
    sys.path.insert(0,str(ROOT/'tools'))
    spec=importlib.util.spec_from_file_location('pc_archive_additive_contract',ARCHIVE)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.ArchiveWindow.__bases__[0].__name__=='Toplevel'
    assert callable(module.ArchiveWindow.open_selected_hit)
    assert callable(module.open_branch_tree_window)
