"""R18 one-app contract, safety guard and legacy compatibility."""
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]


def test_central_launcher_and_single_batch():
    assert len(list(ROOT.rglob('*.bat')))==1
    text=(ROOT/'START_WINDOWS_MENUE.bat').read_text()
    assert 'call :START_CENTER D' in text
    assert 'klrw.control_center --tab %~1' in text
    assert 'if /I "%~1"=="--menu" goto MENU' in text
    for key in 'ABCDE':
        assert f':{dict(A="CAPACITY",B="CLASSIC",C="RECOVERY",D="DRIVE_LED",E="WORKSPACE")[key]}' in text


def test_default_tab_is_d_and_all_views_registered():
    text=(ROOT/'src/klrw/control_center.py').read_text()
    assert "default='D'" in text
    for key in ('D','E','A','B','C','STATUS'):
        assert f"self.panels['{key}']" in text
    assert 'DriveWorkspaceWindow(root,host=' in text
    assert 'DriveLedWindow(root,host=' in text
    assert 'ClassicApp(root,host=' in text


def test_standalone_entries_still_present():
    for mod in ('drive_led_window','drive_workspace_window','gui'):
        text=(ROOT/'src/klrw'/f'{mod}.py').read_text()
        assert 'def main(' in text
        assert 'host=None' in text
        assert 'self.embedded' in text


def test_hardware_exclusive_claim_and_release():
    from klrw import hardware_lease as guard
    guard.release('D');guard.release('B')
    guard.claim('D')
    assert guard.current_owner()=='D'
    with pytest.raises(RuntimeError,match='anderen Bereich'):
        guard.claim('B')
    assert guard.current_owner()=='D'
    guard.release('B')
    assert guard.current_owner()=='D'
    guard.release('D')
    assert guard.current_owner() is None
    guard.claim('B');guard.release('B')


def test_no_implicit_hardware_activation():
    text=(ROOT/'src/klrw/control_center.py').read_text()
    assert 'enable_hardware(' not in text
    assert 'hardware=True' not in text
    assert 'askyesno' in text
    assert 'self.tabs.select(self.panels[\'D\'])' in text


def test_tool_action_allowlist():
    from klrw.control_center import TOOL_ACTIONS
    assert TOOL_ACTIONS=={'Diagnose','Setup','Update','PythonRecovery'}
