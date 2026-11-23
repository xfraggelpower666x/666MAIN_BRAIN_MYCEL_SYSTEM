import pytest
from types import SimpleNamespace
from klrw.network_directions import NetworkDirectionSampler, NetworkRates, states
from klrw.rgb_profiles import parse_profile
from klrw.status_snapshot import lock_tiles, network_tiles, disk_tiles
from klrw.lock_indicator import LockSnapshot
from klrw.ssd import DiskRates

class FakePS:
    def __init__(self): self.rx=100;self.tx=40
    def net_io_counters(self, pernic=False):
        item=SimpleNamespace(bytes_recv=self.rx,bytes_sent=self.tx)
        return {'Ethernet':item} if pernic else item

def test_network_first_sample_zero():
    ps=FakePS();sampler=NetworkDirectionSampler(ps,clock=lambda:10)
    assert sampler.interfaces()==('Ethernet',)
    assert sampler.sample('Ethernet').rx_bps==0

def test_network_rates():
    ps=FakePS();ticks=iter([1,3]);sampler=NetworkDirectionSampler(ps,clock=lambda:next(ticks))
    sampler.sample('Ethernet');ps.rx=300;ps.tx=100
    assert sampler.sample('Ethernet')==NetworkRates('Ethernet',100,30)

def test_network_missing():
    assert NetworkDirectionSampler(FakePS(),clock=lambda:1).sample('unknown').rx_bps==0

def test_network_states():
    assert states(NetworkRates('x',10,2))=={'caps':True,'scroll':True}
    assert states(NetworkRates('x',0,2),threshold_bps=3)=={'caps':False,'scroll':False}

def test_network_overlap_denied():
    with pytest.raises(ValueError): states(NetworkRates('x',1,1),'caps','caps')

def test_profile_normal():
    assert parse_profile('{"3":"ABCDEF","1":"0000ff"}').as_dict()=={'1':'#0000ff','3':'#abcdef'}

@pytest.mark.parametrize('value',['[]','{"1":"fff"}','{"x":"ffffff"}','{"1":"abcdef","1":"ffffff"}','{"125":"ffffff"}','{"01":"ffffff"}'])
def test_profile_rejects_invalid(value):
    with pytest.raises(ValueError): parse_profile(value)

def test_profile_empty():
    assert parse_profile('{}').keys==()

def test_status_lock_order():
    tiles=lock_tiles(LockSnapshot(True,False,True),'SC')
    assert [x.name for x in tiles]==['scroll','caps']
    assert all(x.active for x in tiles)

def test_status_net():
    assert [t.active for t in network_tiles(NetworkRates('x',0,9))]==[False,True]

def test_status_disk():
    assert [t.active for t in disk_tiles(DiskRates('c',5,0))]==[True,False]
