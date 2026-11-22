from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PS=(ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8')
BAT=(ROOT/'START_WINDOWS_MENUE.bat').read_text(encoding='utf-8')

def test_single_batch():
    assert len(list(ROOT.rglob('*.bat')))==1

def test_no_blanket_windowsapps_exclusion():
    assert "-or $path -match" not in PS
    assert 'Invoke-PythonCheck $candidate.path $candidate.args' in PS

def test_manual_python_is_validated():
    assert "Read-Host 'Pfad zu vorhandener python.exe" in PS
    assert 'Invoke-PythonCheck $manual @()' in PS
    assert "Test-Path -LiteralPath $manual -PathType Leaf" in PS

def test_report_contains_candidate_evidence():
    assert 'python_candidates=@()' in PS
    assert '$report.python_candidates +=' in PS

def test_existing_setup_opt_in_preserved():
    assert "Confirm 'Python 3.13 ueber winget" in PS
    assert 'WINDOWS MENUE 7' in BAT
