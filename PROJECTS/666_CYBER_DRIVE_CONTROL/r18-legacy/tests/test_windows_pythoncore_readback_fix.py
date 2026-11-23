from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8-sig')

def test_version_readback_uses_proven_windows_command():
    assert "@('--version')" in SRC
    assert 'function Invoke-PythonCheck' in SRC
    assert 'python version check failed:' in SRC

def test_registry_inventory_location_is_tested_directly():
    assert 'uninstall-location direct candidate:' in SRC
    assert "Join-Path $location 'python.exe'" in SRC
    assert SRC.index('uninstall-location direct candidate:') < SRC.index('# Offizielle Installer schreiben')

def test_installation_does_not_repeat_when_registered():
    assert "if ($registered.Count -gt 0)" in SRC
    assert "winget.exe install --id Python.Python.3.13" in SRC
