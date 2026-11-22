import pytest
from klrw.rgb_layers import RGBPolicy, RGBPreview, RED, BLUE, GREEN, PURPLE, OFF, open_rgb_hardware, RGBHardwareUnavailable
from klrw.rgb_cli import main


def test_layer_zero_off():
    assert RGBPolicy().render().color == OFF


def test_three_colors():
    p = RGBPolicy()
    assert [p.render((i,)).color for i in (1, 2, 3)] == [BLUE, GREEN, PURPLE]


def test_caps_overrides_layer_three():
    f = RGBPolicy().render((3,), True)
    assert f.color == RED and f.source == 'caps_lock'


def test_caps_clear_restores_layer():
    p = RGBPolicy()
    assert p.render((2,), True).color == RED
    assert p.render((2,), False).color == GREEN


def test_highest_active_layer():
    assert RGBPolicy().render((1, 3, 2)).color == PURPLE


def test_independent_units():
    p = RGBPreview(2)
    p.update(0, (1,))
    assert tuple(f.color for f in p.snapshot()) == (BLUE, OFF)


def test_synchronized_units():
    p = RGBPreview(2, synchronized=True)
    assert all(f.color == GREEN for f in p.update(1, (2,)))


def test_invalid_layer_is_rejected():
    with pytest.raises(ValueError): RGBPolicy().render((4,))


def test_invalid_color_rejected():
    with pytest.raises(ValueError): RGBPolicy({0: (0,0,0),1:(0,0,0),2:(0,0,0),3:(256,1,1)})


def test_invalid_unit_rejected():
    with pytest.raises(IndexError): RGBPreview(2).update(3, (1,))


def test_hardware_fail_closed():
    with pytest.raises(RGBHardwareUnavailable): open_rgb_hardware()


def test_cli_preview(capsys):
    assert main(['--layer','3','--caps','--sync']) == 0
    assert '"#FF0000"' in capsys.readouterr().out
