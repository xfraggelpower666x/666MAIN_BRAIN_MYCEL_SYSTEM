"""MENU3 Regression: Ein ueberfluessiges Endquote darf nicht mehr aus CMD kommen."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def test_batch_calls_tool_manager_without_projectroot_native_argument():
    batch=(ROOT/'START_WINDOWS_MENUE.bat').read_text()
    assert '-File "%MANAGER%" -Action %~1' in batch
    assert '-ProjectRoot' not in batch

def test_manager_derives_root_from_own_location():
    ps=(ROOT/'TOOLS'/'WINDOWS_TOOL_MANAGER.ps1').read_text()
    assert "[string]$ProjectRoot=''" in ps
    assert 'Split-Path -Parent $PSScriptRoot' in ps
    assert 'Resolve-Path -LiteralPath $ProjectRoot' in ps
    assert '.ProviderPath' in ps

def test_all_menu_actions_use_same_tool_boundary():
    b=(ROOT/'START_WINDOWS_MENUE.bat').read_text()
    assert b.count('powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%MANAGER%" -Action %~1')==1
    for action in ('Diagnose','Setup','Update'):
        assert 'call :TOOLACTION '+action in b

def test_only_one_batch_and_still_one_manager():
    assert len(list(ROOT.rglob('*.bat')))==1
    assert (ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').is_file()

def test_no_software_or_hardware_mutation_added():
    a=(ROOT/'START_WINDOWS_MENUE.bat').read_text().lower()
    assert 'rmdir /s' not in a and 'del /f' not in a
    ps=(ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text().lower()
    assert 'remove-item' not in ps
