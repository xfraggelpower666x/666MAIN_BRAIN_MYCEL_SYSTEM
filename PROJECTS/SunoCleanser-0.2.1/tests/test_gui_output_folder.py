from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import Mock

import pytest
from sunocleanser.gui import app


@pytest.mark.parametrize(
    ("platform", "launcher"), [("linux", "xdg-open"), ("darwin", "open"), ("win32", "startfile")]
)
def test_missing_folder_launcher_shows_path(monkeypatch, tmp_path, platform, launcher):
    output = tmp_path / "out"
    view = Mock()
    showinfo = Mock()
    launch = Mock(side_effect=FileNotFoundError(launcher))
    monkeypatch.setattr(app, "OUT_DIR", output)
    monkeypatch.setattr(app.sys, "platform", platform)
    if platform == "win32":
        monkeypatch.setattr(app.os, "startfile", launch, raising=False)
    else:
        monkeypatch.setattr(app.subprocess, "run", launch)
    monkeypatch.setattr(app.messagebox, "showinfo", showinfo)

    app.SunoCleanserApp._open_out(view)

    assert output.is_dir()
    view._text.assert_called_once_with("folder", path=output.resolve())
    showinfo.assert_called_once_with("SunoCleanser", view._text.return_value)


@pytest.mark.parametrize("returncode", [0, 1])
def test_folder_launcher_result(monkeypatch, tmp_path, returncode):
    output = tmp_path / "out"
    showinfo = Mock()
    launch = Mock(return_value=CompletedProcess([], returncode))
    monkeypatch.setattr(app, "OUT_DIR", output)
    monkeypatch.setattr(app.sys, "platform", "linux")
    monkeypatch.setattr(app.subprocess, "run", launch)
    monkeypatch.setattr(app.messagebox, "showinfo", showinfo)

    app.SunoCleanserApp._open_out(Mock())

    launch.assert_called_once_with(["xdg-open", Path(output).resolve()], check=False)
    assert showinfo.call_count == returncode
