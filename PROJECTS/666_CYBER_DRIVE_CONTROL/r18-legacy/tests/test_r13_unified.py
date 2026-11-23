"""Pure integration tests, without Windows, HID or tray runtime."""
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
import pytest
from klrw.lock_indicator import LockSnapshot, PreviewLockReader
from klrw.ssd import DiskRates
from klrw.network_directions import NetworkRates
from klrw.unified_state import compose_frame, icon_colors
from klrw.unified_tray import UnifiedSampler, render_icon


def frame(**options):
    return compose_frame(LockSnapshot(True,False,True),DiskRates('_total',2048,8192),
                         NetworkRates('_total',1024,0),34,67,**options)


def test_lock_states_and_activity():
    f=frame()
    assert [(x.name,x.active) for x in f.tiles] == [
        ('num',False),('caps',True),('scroll',True),('read',True),
        ('write',True),('rx',True),('tx',False)]


def test_rgb_caps_overrides_layer():
    assert frame(layer=3).rgb==(255,0,0)
    assert frame(layer=3).rgb_source=='caps_lock'


def test_rgb_preview_without_caps():
    f=compose_frame(LockSnapshot(False,False,False),DiskRates('d',0,0),
                    NetworkRates('n',0,0),layer=3)
    assert f.rgb==(150,0,230)


def test_order_and_hide():
    assert [x.name for x in frame(order='SC').tiles[:2]]==['scroll','caps']
    assert len(frame(order='').tiles)==4


@pytest.mark.parametrize('kwargs',[{'layer':4},{'layer':1.0},{'order':'CC'},
                                   {'disk_threshold_bps':-1},{'network_threshold_bps':-1},
                                   {'cpu_pct':float('nan')}])
def test_invalid_inputs(kwargs):
    with pytest.raises((ValueError,TypeError)):frame(**kwargs)


def test_negative_rates_are_clamped():
    f=compose_frame(LockSnapshot(False,False,False),DiskRates('d',-7,-4),NetworkRates('n',-1,-2))
    assert f.disk.read_bps==f.disk.write_bps==f.network.rx_bps==f.network.tx_bps==0


def test_change_fingerprint():
    assert frame().fingerprint==frame().fingerprint
    assert frame(layer=3).fingerprint!=frame(layer=0).fingerprint


def test_color_matrix():
    colors=icon_colors(frame());assert len(colors)==9
    assert colors[0]!=colors[1] and colors[3]!=colors[8]


def test_immutable_frame():
    with pytest.raises(FrozenInstanceError):frame().layer=3


def test_preview_sampler_no_real_queries():
    class Forbidden:
        def sample(self,*a,**kw):raise AssertionError('Actual sensor called')
    sampler=UnifiedSampler(reader=PreviewLockReader(),system=Forbidden(),disks=Forbidden(),
                           network=Forbidden(),preview=True)
    f=sampler.sample(layer=2)
    assert f.disk.read_bps>0 and f.network.rx_bps>0 and f.rgb_source=='layer'


def test_mock_live_sampler():
    class Fixed:
        def __init__(self,value):self.value=value
        def sample(self,*args):return self.value
    sampler=UnifiedSampler(reader=PreviewLockReader(caps=True),
        system=Fixed(SimpleNamespace(cpu=14,memory=51)),
        disks=Fixed(DiskRates('disk',100,0)),network=Fixed(NetworkRates('net',0,500)))
    f=sampler.sample()
    assert f.cpu_pct==14 and f.memory_pct==51 and f.rgb_source=='caps_lock'


def test_icon_render():
    pytest.importorskip('PIL')
    i=render_icon(frame());assert i.size==(64,64) and i.mode=='RGBA'
    with pytest.raises(ValueError):render_icon(frame(),size=8)
