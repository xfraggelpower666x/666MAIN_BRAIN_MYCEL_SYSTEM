"""Static contract regression for additive dual-EXE Windows packaging."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_original_main_pyinstaller_spec_is_preserved():
    spec = (ROOT / "666_CHATBACKUP_PC_TOOL.spec").read_text(encoding="utf-8")
    assert 'chatbackup_gui.pyw' in spec
    assert 'name="666_CHATBACKUP_PC_TOOL"' in spec

def test_archive_companion_has_independent_spec():
    spec = (ROOT / "666_CHATBACKUP_ARCHIVE_INTELLIGENCE.spec").read_text(encoding="utf-8")
    assert "archive_intelligence_gui.py" in spec
    assert 'name="666_CHATBACKUP_ARCHIVE_INTELLIGENCE"' in spec
    assert 'str(app_dir)' in spec

def test_existing_local_build_produces_both_exes():
    bat = (ROOT / "BUILD_EXE.bat").read_text(encoding="utf-8")
    assert '"666_CHATBACKUP_PC_TOOL.spec"' in bat
    assert '"666_CHATBACKUP_ARCHIVE_INTELLIGENCE.spec"' in bat
    assert "dist\\666_CHATBACKUP_PC_TOOL.exe" in bat
    assert "dist\\666_CHATBACKUP_ARCHIVE_INTELLIGENCE.exe" in bat

def test_both_gui_variants_prefer_packaged_companion_and_preserve_source_fallback():
    for name in ("chatbackup_gui.py", "chatbackup_gui.pyw"):
        text = (ROOT / "app" / name).read_text(encoding="utf-8")
        method = text.split("    def open_archive_intelligence(self) -> None:", 1)[1].split("    def show_log(self)", 1)[0]
        exe = method.index('companion.is_file()')
        source = method.index('script = project_root / "tools"')
        assert exe < source, name
        assert '666_CHATBACKUP_ARCHIVE_INTELLIGENCE.exe' in method
        assert 'subprocess.Popen([str(companion)]' in method
        assert '"archive_intelligence_gui.py"' in method
