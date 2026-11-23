from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MANAGER = (ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8-sig')
BAT = (ROOT/'START_WINDOWS_MENUE.bat').read_text(encoding='utf-8')

def test_one_batch_and_preserved_actions():
    assert len(list(ROOT.rglob('*.bat'))) == 1
    for action in ('Diagnose','Setup','Update','Verify','PythonRecovery'):
        assert action in MANAGER
    assert ('choice /c 123456789ABC0' in BAT or 'choice /c 123456789ABCD0' in BAT or 'choice /c 123456789ABCDE0' in BAT)
    assert 'goto RECOVERY' in BAT

def test_registered_package_is_not_executable():
    assert 'PYTHON_REGISTERED_EXECUTABLE_UNVERIFIED' in MANAGER
    assert "if ($registered.Count -gt 0)" in MANAGER
    assert 'winget.exe install' in MANAGER
    assert 'Get-InstalledPythonPackages' in MANAGER

def test_persistent_diagnostic_evidence():
    assert 'python_registry_hints' in MANAGER
    assert 'python_scan_roots' in MANAGER
    assert 'python_candidates' in MANAGER
    assert 'execution_or_version_failed' in MANAGER

def test_file_picker_is_optional():
    assert 'System.Windows.Forms.OpenFileDialog' in MANAGER
    assert "if ($manual -eq '?')" in MANAGER
    assert 'Test-Path -LiteralPath $manual -PathType Leaf' in MANAGER

def test_no_destructive_repair_without_user():
    assert '& $pkg.uninstall' not in MANAGER
    assert 'winget.exe uninstall' not in MANAGER
    assert 'Remove-Item -Recurse' not in MANAGER
    assert "if (-not (Confirm 'Python 3.13" in MANAGER

def test_real_readback_before_ready():
    assert 'Invoke-PythonCheck' in MANAGER
    assert "$report.result='READY'" in MANAGER
    assert 'RunPython $choice' in MANAGER
