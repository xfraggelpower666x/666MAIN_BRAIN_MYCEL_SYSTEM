"""Statische Abnahmetests für den Windows-Starter (Windows-Laufzeit separat prüfen)."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'START_WINDOWS_MENUE.bat'
MANAGER=ROOT/'TOOLS'/'WINDOWS_TOOL_MANAGER.ps1'


def test_single_batch():
    assert [p.name for p in ROOT.rglob('*.bat')] == ['START_WINDOWS_MENUE.bat']


def test_batch_uses_local_virtualenv():
    text=BATCH.read_text()
    assert r'.venv\Scripts\python.exe' in text
    assert '"%ENV%" -m klrw.unified_tray' in text
    assert '"%ENV%" -m pytest -q' in text


def test_menu_has_real_install_and_update():
    text=BATCH.read_text()
    for label in ('DIAG','SETUP','UPDATE','TRAY','PREVIEW','TESTS','READBACK','CHECK_READBACK','DASHBOARD','CAPACITY','CLASSIC'):
        assert re.search(r'^:'+label+r'\r?$',text,re.M)
    assert '-Action %~1' in text


def test_setup_uses_powershell_helper():
    text=BATCH.read_text()
    assert 'call :TOOLACTION Setup' in text
    assert 'call :TOOLACTION Update' in text


def test_store_alias_is_not_accepted():
    source=MANAGER.read_text()
    assert r'WindowsApps\\' in source
    assert 'Invoke-PythonCheck' in source
    assert 'sys.version_info >= (3,10)' in source


def test_install_needs_consent():
    source=MANAGER.read_text()
    assert "Confirm 'Python 3.13 ueber winget installieren" in source
    assert "Confirm 'Fehlende Projekt-, Tray- und Testpakete" in source
    assert 'winget.exe install --id Python.Python.3.13' in source


def test_update_needs_consent():
    source=MANAGER.read_text()
    assert "Confirm 'Lokale pip-/Projekt-Abhaengigkeiten jetzt aktualisieren?" in source
    assert '-m pip install --upgrade' in source


def test_no_venv_deletion():
    source=MANAGER.read_text()
    assert 'Remove-Item' not in source
    assert 'defekte' not in BATCH.read_text().lower()


def test_required_and_optional_tools():
    source=MANAGER.read_text()
    for item in ('klrw','psutil','pystray','PIL','pytest','winget.exe','smartctl.exe','setuptools','wheel','build'):
        assert item in source


def test_json_readback():
    assert "ConvertTo-Json -Depth 8" in MANAGER.read_text()
    assert 'TOOLS\\REPORTS' in MANAGER.read_text()


def test_readback_uses_same_venv():
    text=BATCH.read_text()
    assert '-PythonExe "%ENV%"' in text
    assert '-PreviewOnly' in text


def test_no_firmware_or_driver_install():
    source=MANAGER.read_text().lower()
    for word in ('pnputil','devcon','flashrom','rmmod','insmod'):
        assert word not in source
