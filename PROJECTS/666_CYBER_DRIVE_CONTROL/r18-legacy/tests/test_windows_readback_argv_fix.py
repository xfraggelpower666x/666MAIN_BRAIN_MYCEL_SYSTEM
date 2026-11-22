"""Regression: Windows PowerShell 5.1 must not strip quotes in Python -c readback."""
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'TOOLS' / 'WINDOWS_TOOL_MANAGER.ps1'


def test_readback_python_code_avoids_nested_string_quotes():
    script = SCRIPT.read_text(encoding='utf-8-sig')
    assert "& $venv -c 'import klrw.unified_tray, klrw.unified_state, psutil, pystray, PIL, pytest'" in script
    assert 'Note \'[OK] Unified Tray und alle Abhaengigkeiten importierbar.\'' in script
    assert 'pytest; print("[OK]' not in script


def test_upgrade_installs_optional_build_tool():
    script = SCRIPT.read_text(encoding='utf-8-sig')
    assert '& $venv -m pip install --upgrade pip setuptools wheel build' in script
    assert "if ($LASTEXITCODE -ne 0) { throw 'pip-Toolupdate fehlgeschlagen' }" in script
