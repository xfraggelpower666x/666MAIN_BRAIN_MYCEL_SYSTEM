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


def test_audio_picker_includes_mp3(monkeypatch):
    view = Mock()
    view._text.side_effect = lambda key: {
        "select_audio": "Select audio",
        "all_files": "All files",
    }[key]
    chooser = Mock(return_value="")
    monkeypatch.setattr(app.filedialog, "askopenfilename", chooser)

    app.SunoCleanserApp._browse(view)

    chooser.assert_called_once_with(
        title="Select audio",
        filetypes=[("WAV and MP3", "*.wav *.mp3"), ("All files", "*.*")],
    )
