from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8')

def test_installed_inventory_from_registry_and_winget():
    assert 'function Get-InstalledPythonPackages' in s
    assert 'function Get-WingetPythonInventory' in s
    assert 'winget.exe list --id Python.Python.3.13' in s

def test_prevent_repeat_install_when_existing_package():
    guard=s.index('if ($registered.Count -gt 0)')
    install=s.index('winget.exe install --id Python.Python.3.13')
    assert guard < install
    assert "[BLOCKIERT] Windows meldet Python bereits als installiert" in s

def test_registry_location_and_report_evidence():
    assert "Join-Path $pkg.location 'python.exe'" in s
    assert 'installed_python_packages' in s
    assert "[INVENTAR]" in s

def test_one_batch_entrypoint():
    assert len(list(root.rglob('*.bat')))==1
    assert 'WINDOWS MENUE 7' in (root/'START_WINDOWS_MENUE.bat').read_text()
