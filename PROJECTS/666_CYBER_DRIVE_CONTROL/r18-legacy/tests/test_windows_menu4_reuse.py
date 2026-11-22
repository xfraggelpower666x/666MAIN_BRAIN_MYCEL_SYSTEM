from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS = (ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8')
BAT = (ROOT/'START_WINDOWS_MENUE.bat').read_text(encoding='utf-8')

def test_single_batch_entry():
    assert [p.name for p in ROOT.rglob('*.bat')] == ['START_WINDOWS_MENUE.bat']

def test_python_search_reuses_venv_and_winget():
    assert "Add-Candidate $venv" in PS
    assert "Microsoft\\WinGet\\Packages" in PS
    assert "-0p" in PS
    assert "PythonCore" in PS

def test_no_unattended_global_python_upgrade():
    assert "Confirm 'Python 3.13 ueber winget" in PS
    assert 'winget.exe upgrade ' not in PS
    assert "Keine erneute Installation erforderlich" in PS

def test_batch_starts_manager_without_path_argument():
    assert '"%MANAGER%" -Action %~1' in BAT
    assert '-ProjectRoot ' not in BAT
