from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS = (ROOT / 'TOOLS/WINDOWS_TOOL_MANAGER.ps1').read_text(encoding='utf-8')
BAT = (ROOT / 'START_WINDOWS_MENUE.bat').read_text(encoding='utf-8')


def test_winget_output_is_not_function_return_value():
    assert '--disable-interactivity | Out-Host' in PS
    assert '$installExit = $LASTEXITCODE' in PS
    assert '$report.winget_install_exit = $installExit' in PS


def test_python_choice_checked_before_venv():
    assert '$choice -isnot [hashtable]' in PS
    assert 'Ensure-Venv $choice' in PS


def test_winget_success_does_not_claim_python_found():
    assert "$report.result='READBACK_PENDING'" in PS
    assert "if ($report.result -ne 'READBACK_PENDING')" in PS


def test_entrypoint_single_batch_and_no_projectroot_arg():
    assert len(list(ROOT.rglob('*.bat'))) == 1
    assert 'WINDOWS MENUE 7' in BAT
    assert ' -ProjectRoot ' not in BAT
