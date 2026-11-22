from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "TOOLS" / "WINDOWS_TOOL_MANAGER.ps1").read_text(encoding="utf-8-sig")

def test_native_process_with_separate_streams():
    assert "System.Diagnostics.ProcessStartInfo" in SOURCE
    assert "$start.RedirectStandardOutput = $true" in SOURCE
    assert "$start.RedirectStandardError = $true" in SOURCE
    section = SOURCE.split("function Invoke-PythonCheck",1)[1].split("# Ermittelt bereits",1)[0]
    assert "2>&1" not in section

def test_exit_timeout_and_version_validation():
    assert "$process.WaitForExit(10000)" in SOURCE
    assert "$exitCode -eq 0 -and $versionMatch.Success" in SOURCE
    assert "$minor -ge 10" in SOURCE

def test_failure_evidence_is_not_suppressed():
    assert "python version check failed:" in SOURCE
    assert "stdout=" in SOURCE and "stderr=" in SOURCE
    assert "python version exception:" in SOURCE

def test_already_installed_python_still_no_blind_reinstall():
    assert "Get-InstalledPythonPackages" in SOURCE
    assert "[BLOCKIERT] Windows meldet Python" in SOURCE

def test_no_change_to_pythoncore_discovery():
    assert "pythoncore direct candidate:" in SOURCE
    assert "Invoke-PythonCheck $candidate.path $candidate.args" in SOURCE
