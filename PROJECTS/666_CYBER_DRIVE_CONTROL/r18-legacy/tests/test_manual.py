import json
import pytest
from klrw.manual import ManualLedController
from klrw.ledctl import main

@pytest.mark.parametrize('led', ['caps','num','scroll'])
def test_manual_preview_each_led(led):
    with ManualLedController() as ctl:
        assert ctl.state(led).state is False
        assert ctl.set(led, True).state is True
        assert ctl.set(led, False).state is False

def test_validation_and_lifecycle():
    ctl = ManualLedController()
    with pytest.raises(ValueError): ctl.set('bad', True)
    with pytest.raises(ValueError): ctl.set('num', 1)
    ctl.close()
    with pytest.raises(RuntimeError): ctl.state('num')

def test_cli_preview(capsys):
    assert main(['scroll','on']) == 0
    assert json.loads(capsys.readouterr().out) == {'led':'scroll','state':True,'source':'preview'}

def test_keep_state_not_allowed_without_hardware():
    with pytest.raises(SystemExit): main(['scroll','on','--keep-state'])

def test_windows_hardware_refused_on_other_systems(monkeypatch):
    import klrw.ledctl as m
    monkeypatch.setattr(m.sys,'platform','linux')
    with pytest.raises(SystemExit): main(['scroll','get','--hardware'])

def test_hardware_write_needs_acknowledgement(monkeypatch):
    import klrw.ledctl as m
    monkeypatch.setattr(m.sys,'platform','win32')
    with pytest.raises(SystemExit): main(['scroll','on','--hardware'])
