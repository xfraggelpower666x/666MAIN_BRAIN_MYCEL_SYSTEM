"""Headless checks for the responsive layout decision and preserved UI contracts."""
from pathlib import Path

from klrw.drive_workspace_window import settings_should_stack


def test_settings_stack_at_narrow_width():
    assert settings_should_stack(720)
    assert settings_should_stack(989)
    assert not settings_should_stack(990)
    assert not settings_should_stack(1280)


def test_fixed_absolute_scrollbar_position_is_gone():
    source = (Path(__file__).resolve().parents[1] / "src" / "klrw" / "drive_workspace_window.py").read_text(encoding="utf-8")
    assert "self.scrollbar.place(" not in source
    assert "self.scrollbar.pack(side='right',fill='y')" in source
    assert "settings_should_stack(event.width)" in source


def test_neon_buttons_have_all_four_actions():
    source = (Path(__file__).resolve().parents[1] / "src" / "klrw" / "drive_workspace_window.py").read_text(encoding="utf-8")
    for label in ("Speichern", "Overlay zeigen", "Jetzt neu erkennen", "Einstellungen anwenden"):
        assert label in source
    assert "tk.Button(parent" in source
    assert "theme_use('clam')" in source
