from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "TOOLS/WINDOWS_TOOL_MANAGER.ps1").read_text(encoding="utf-8-sig")

def test_registry_views_both_architectures():
    assert "RegistryView]::Registry64" in SRC
    assert "RegistryView]::Registry32" in SRC
    assert "ExecutablePath" in SRC

def test_uninstall_metadata_never_executed():
    assert "DisplayIcon" in SRC
    assert "InstallSource" in SRC
    assert "if ($registered.Count -gt 0)" in SRC
    assert "PYTHON_REGISTERED_EXECUTABLE_UNVERIFIED" in SRC
    assert "& $pkg.uninstall" not in SRC

def test_missing_interpreter_candidates_reported():
    assert "reason='not_found'" in SRC
    assert "registry_python_paths" in SRC

def test_single_batch_entrypoint():
    assert len(list(ROOT.rglob("*.bat"))) == 1
