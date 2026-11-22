"""Single-tool contract: original v1.10.5 app, one EXE, one user-facing menu."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_original_main_pyinstaller_spec_is_preserved():
    spec = (ROOT / "666_CHATBACKUP_PC_TOOL.spec").read_text(encoding="utf-8")
    assert 'chatbackup_gui.pyw' in spec
    assert 'name="666_CHATBACKUP_PC_TOOL"' in spec
    assert "str(tools_dir)" in spec

def test_optional_companion_source_preserved_for_compatibility():
    assert (ROOT / "666_CHATBACKUP_ARCHIVE_INTELLIGENCE.spec").exists()

def test_local_build_generates_exactly_one_original_exe():
    bat = (ROOT / "BUILD_EXE.bat").read_text(encoding="utf-8")
    assert '"666_CHATBACKUP_PC_TOOL.spec"' in bat
    assert '"666_CHATBACKUP_ARCHIVE_INTELLIGENCE.spec"' not in bat
    assert r"dist\666_CHATBACKUP_PC_TOOL.exe" in bat
    assert r"dist\666_CHATBACKUP_ARCHIVE_INTELLIGENCE.exe" not in bat

def test_single_windows_menu_has_real_commands():
    bat=(ROOT/"666_CHATBACKUP_MENUE.bat").read_text(encoding="utf-8")
    for token in (':menu', ':build', ':runexe', ':runpy', ':diag',
                  ':deps', ':tests', ':integrity', ':acceptance'):
        assert token in bat
    assert '"666_CHATBACKUP_PC_TOOL.spec"' in bat
    assert '"666_CHATBACKUP_ARCHIVE_INTELLIGENCE.spec"' not in bat

def test_both_gui_versions_use_inprocess_archive_and_left_status_only():
    for name in ("chatbackup_gui.py", "chatbackup_gui.pyw"):
        text = (ROOT / "app" / name).read_text(encoding="utf-8")
        method=text.split("    def open_archive_intelligence(self) -> None:", 1)[1].split("    def show_log(self)",1)[0]
        assert "ArchiveWindow(master=self)" in method
        assert "subprocess.Popen" not in method
        assert "666_CHATBACKUP_ARCHIVE_INTELLIGENCE.exe" not in method
        assert 'command=self.show_system_status' in text.split("    def _build_sidebar(",1)[1].split("    def _section_title(",1)[0]
        footer=text.split("    def _build_footer(",1)[1].split("    def _on_root_configure(",1)[0]
        assert 'command=self.show_system_status' not in footer
        assert "textvariable=self.status_var" in footer
