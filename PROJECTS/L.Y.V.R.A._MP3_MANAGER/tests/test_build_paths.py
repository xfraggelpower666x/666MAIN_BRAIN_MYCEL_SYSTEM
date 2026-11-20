import shutil
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import SYSTEM_CHECK
from VERIFY_PORTABLE_FOLDER import REQUIRED_FILES, verify


@pytest.mark.skipif(sys.platform != "win32", reason="Windows batch launcher")
def test_build_launcher_runs_project_check_from_another_directory(tmp_path):
    project = tmp_path / "project with spaces"
    project.mkdir()
    shutil.copy2(ROOT / "L.Y.V.R.A._MP3_MANAGER.bat", project / "L.Y.V.R.A._MP3_MANAGER.bat")
    subprocess.run([sys.executable, "-m", "venv", str(project / ".venv_stable")], check=True)
    (project / "SYSTEM_CHECK.py").write_text(
        "import os, pathlib, sys\n"
        "arg = sys.argv[1] if len(sys.argv) > 1 else 'check'\n"
        "with pathlib.Path('calls.txt').open('a') as f: f.write(arg + '\\n')\n"
        "if arg == 'check' and os.environ.get('FAIL_CHECK'): sys.exit(7)\n"
        "if arg == '--build':\n"
        " p=pathlib.Path('dist/L.Y.V.R.A._MP3_MANAGER/L.Y.V.R.A._MP3_MANAGER.exe')\n"
        " p.parent.mkdir(parents=True); p.write_bytes(b'MZ')\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["cmd.exe", "/c", str(project / "L.Y.V.R.A._MP3_MANAGER.bat"), "build", "/nopause"],
        cwd=tmp_path, text=True, capture_output=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "calls.txt").read_text().splitlines() == ["--build-check", "--build"]
    start = subprocess.run(
        ["cmd.exe", "/c", str(project / "L.Y.V.R.A._MP3_MANAGER.bat"), "start", "/nopause"],
        cwd=tmp_path, text=True, capture_output=True, timeout=60,
    )
    assert start.returncode == 0, start.stdout + start.stderr
    assert (project / "calls.txt").read_text().splitlines()[-2:] == ["check", "--launch"]
    check = subprocess.run(
        ["cmd.exe", "/c", str(project / "L.Y.V.R.A._MP3_MANAGER.bat"), "check", "/nopause"],
        cwd=tmp_path, env={**os.environ, "FAIL_CHECK": "1"}, text=True,
        capture_output=True, timeout=30,
    )
    assert check.returncode == 7


@pytest.mark.skipif(sys.platform != "win32", reason="Windows batch launcher")
def test_portable_verification_and_invalid_action(tmp_path):
    shutil.copy2(ROOT / "L.Y.V.R.A._MP3_MANAGER.bat", tmp_path / "L.Y.V.R.A._MP3_MANAGER.bat")
    (tmp_path / "L.Y.V.R.A._MP3_MANAGER.exe").write_bytes(b"MZ")
    verifier = tmp_path / "PORTABLE_VERIFY.ps1"
    verifier.write_text("exit 7\n", encoding="ascii")
    command = ["cmd.exe", "/c", str(tmp_path / "L.Y.V.R.A._MP3_MANAGER.bat")]
    result = subprocess.run(command + ["verify", "/nopause"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 7
    verifier.write_text("exit 0\n", encoding="ascii")
    result = subprocess.run(command + ["verify", "/nopause"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    result = subprocess.run(command + ["invalid", "/nopause"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    result = subprocess.run(command + ["check", "/nopause"], capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "vollstaendige Quellprojekt" in result.stdout
    result = subprocess.run(command, input="6\n", capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    tools = tmp_path / "tools"
    tools.mkdir()
    not_ffmpeg = Path(os.environ["SystemRoot"]) / "System32" / "where.exe"
    shutil.copy2(not_ffmpeg, tools / "ffmpeg.exe")
    shutil.copy2(not_ffmpeg, tools / "ffprobe.exe")
    result = subprocess.run(command + ["audio", "/nopause"], capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "libmp3lame nicht nutzbar" in result.stdout


def test_build_copies_required_portable_batch_files(tmp_path):
    for name in (
        "BEDIENUNGSANLEITUNG_DE.md", "MANUAL_EN.md", "README.txt",
        "L.Y.V.R.A._MP3_MANAGER.bat", "PORTABLE_VERIFY.ps1",
        "HOST_ABNAHME_WINDOWS.bat", "HOST_ABNAHME_WINDOWS.ps1",
    ):
        shutil.copy2(ROOT / name, tmp_path / name)
    shutil.copytree(ROOT / "assets", tmp_path / "assets")
    for name in ("ffmpeg.exe", "ffprobe.exe"):
        (tmp_path / name).write_bytes(b"MZ")

    def fake_pyinstaller(cmd, cwd):
        assert cwd == str(tmp_path)
        data = [cmd[i + 1] for i, value in enumerate(cmd) if value == "--add-data"]
        assert any("RestorationLab.png" in value and "restoration_lab" in value for value in data)
        assert any("legacy_app.py" in value and "restoration_lab" in value for value in data)
        portable = Path(cmd[cmd.index("--distpath") + 1]) / cmd[cmd.index("--name") + 1]
        portable.mkdir(parents=True)
        (portable / "L.Y.V.R.A._MP3_MANAGER.exe").write_bytes(b"MZ")
        for rel in REQUIRED_FILES:
            if rel.startswith("_internal/"):
                bundled = portable / rel
                bundled.parent.mkdir(parents=True, exist_ok=True)
                bundled.write_bytes(b"build fixture")
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
