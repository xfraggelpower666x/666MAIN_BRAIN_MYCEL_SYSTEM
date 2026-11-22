import pytest
from klrw.drive_led_mapping import DriveBinding, evaluate
from klrw.ssd import DiskRates

def test_all_channels():
    rates={'C:':DiskRates('C:',8192,0),'D:':DiskRates('D:',0,16384)}
    vals=evaluate([DriveBinding('caps','C:','read'),DriveBinding('num','D:','write'),DriveBinding('scroll','C:','either')],rates)
    assert vals == {'caps':True,'num':True,'scroll':True}

def test_off_and_missing_drive():
    assert evaluate([DriveBinding('caps','missing','read'),DriveBinding('num','D:','off')],{'D:':DiskRates('D:',5e6,5e6)}) == {'caps':False,'num':False}

def test_threshold_and_invalid():
    assert not evaluate([DriveBinding('scroll','C:','read',4)],{'C:':DiskRates('C:',4096,0)})['scroll']
    for mode in ('auto','hardware'):
        with pytest.raises(ValueError): evaluate([DriveBinding('caps','C:',mode)],{})

def test_duplicate_rejected():
    with pytest.raises(ValueError): evaluate([DriveBinding('caps','C:'),DriveBinding('caps','D:')],{})

def test_no_default_hardware_and_menu_entry():
    from pathlib import Path
    source=Path(__file__).resolve().parents[1]
    ui=(source/'src/klrw/drive_led_window.py').read_text()
    menu=(source/'START_WINDOWS_MENUE.bat').read_text()
    assert 'self.backend = None' in ui
    assert 'askyesno' in ui
    assert 'self.disable_hardware()' in ui
    assert ('choice /c 123456789ABCD0' in menu or 'choice /c 123456789ABCDE0' in menu)
    assert '"%ENV%" -m klrw.drive_led_window' in menu
