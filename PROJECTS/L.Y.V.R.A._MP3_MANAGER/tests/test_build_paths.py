import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import SYSTEM_CHECK
from VERIFY_PORTABLE_FOLDER import verify


@pytest.mark.skipif(sys.platform != "win32", reason="Windows batch launcher")
def test_build_launcher_runs_project_check_from_another_directory(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for name in ("BUILD_PORTABLE_EXE.bat", "PYTHON_STABLE.bat"):
        shutil.copy2(ROOT / name, project / name)
    subprocess.run([sys.executable, "-m", "venv", str(project / ".venv_stable")], check=True)
    (project / "SYSTEM_CHECK.py").write_text(
        "import pathlib, sys\n"
        "with pathlib.Path('calls.txt').open('a') as f: f.write(sys.argv[1] + '\\n')\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["cmd.exe", "/c", str(project / "BUILD_PORTABLE_EXE.bat")],
        cwd=tmp_path, input="\n", text=True, capture_output=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "calls.txt").read_text().splitlines() == ["--build-check", "--build"]


def test_build_copies_required_portable_batch_files(tmp_path):
    for name in (
        "BEDIENUNGSANLEITUNG_DE.md", "MANUAL_EN.md", "README.txt",
        "REPARATUR_AUDIO_TOOLS.bat", "PORTABLE_VERIFY.bat", "PORTABLE_VERIFY.ps1",
    ):
        shutil.copy2(ROOT / name, tmp_path / name)
    shutil.copytree(ROOT / "assets", tmp_path / "assets")
    for name in ("ffmpeg.exe", "ffprobe.exe"):
        (tmp_path / name).write_bytes(b"MZ")

    def fake_pyinstaller(cmd, cwd):
        assert cwd == str(tmp_path)
        portable = Path(cmd[cmd.index("--distpath") + 1]) / cmd[cmd.index("--name") + 1]
        portable.mkdir(parents=True)
        (portable / "L.Y.V.R.A._MP3_MANAGER.exe").write_bytes(b"MZ")
        (portable / "_internal").mkdir()
        return 0

    def fake_verification(cmd, cwd):
        assert cwd == str(tmp_path)
        assert verify(cmd[-1], platform="linux")["status"] == "STATIC_PASS_WINDOWS_PENDING"
        return subprocess.CompletedProcess(cmd, 0)

    with (
        patch.object(SYSTEM_CHECK, "ROOT", tmp_path),
        patch.object(SYSTEM_CHECK, "check_packages", return_value=True),
        patch.object(SYSTEM_CHECK, "check_audio"),
        patch.object(SYSTEM_CHECK, "check_mp3_encoder", return_value=True),
        patch.object(SYSTEM_CHECK.subprocess, "call", side_effect=fake_pyinstaller),
        patch.object(SYSTEM_CHECK.subprocess, "run", side_effect=fake_verification),
        patch.object(sys, "argv", ["SYSTEM_CHECK.py", "--build"]),
    ):
        assert SYSTEM_CHECK.main() == 0
