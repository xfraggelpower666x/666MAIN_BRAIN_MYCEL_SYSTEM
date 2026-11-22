from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "TOOLS" / "WINDOWS_TOOL_MANAGER.ps1").read_text(encoding="utf-8-sig")

def test_pythoncore_explicit_direct_candidate():
    assert "Join-Path $env:LOCALAPPDATA 'Python'" in SCRIPT
    assert "Join-Path $coreDir.FullName 'python.exe'" in SCRIPT
    assert 'Add-Candidate $coreExe @()' in SCRIPT

def test_pythoncore_before_registry_and_recursive_scan():
    assert SCRIPT.index('pythoncore direct candidate:') < SCRIPT.index('# Offizielle Installer schreiben')
    assert SCRIPT.index('pythoncore direct candidate:') < SCRIPT.index('# winget-Python liegt')

def test_pythoncore_profile_relative_no_fixed_identity():
    section = SCRIPT.split('# B-09:', 1)[1].split('# Offizielle Installer schreiben', 1)[0]
    assert r'C:\Users\dirkm' not in section
    assert "Test-Path -LiteralPath $pythonCoreRoot -PathType Container" in section

def test_pythoncore_semantic_minor_preference():
    assert 'if ($minor -eq 13) { 0 }' in SCRIPT
    assert 'elseif ($minor -eq 14) { 1 }' in SCRIPT
    assert '10 + $minor' in SCRIPT
