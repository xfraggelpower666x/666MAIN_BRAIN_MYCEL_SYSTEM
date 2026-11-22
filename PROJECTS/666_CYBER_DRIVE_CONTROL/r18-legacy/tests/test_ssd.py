import pytest
from types import SimpleNamespace as NS
from klrw.ssd import DiskActivitySampler, DiskRates, IndicatorSettings, indicator_rgb, indicator_hex

class FakePs:
    def __init__(self): self.n = 0
    def disk_io_counters(self, perdisk=False):
        if perdisk:
            return {"C:": NS(read_bytes=self.n*1024, write_bytes=self.n*2048),
                    "D:": NS(read_bytes=0, write_bytes=self.n*100)}
        return NS(read_bytes=self.n*1024, write_bytes=self.n*2048)

def test_devices_and_rates():
    ps=FakePs(); clock=iter((1.,3.)); sampler=DiskActivitySampler(ps,lambda:next(clock))
    assert sampler.devices()==("_total","C:","D:")
    assert sampler.sample("C:")==DiskRates("C:",0.,0.)
    ps.n=2
    assert sampler.sample("C:")==DiskRates("C:",1024.,2048.)

def test_colors_and_saturation():
    settings=IndicatorSettings(saturation_kib=1)
    assert indicator_rgb(DiskRates("_total",1024,1024),settings)==(255,255,0)
    assert indicator_hex(DiskRates("_total",0,0),settings)=="#000000"
    assert indicator_rgb(DiskRates("_total",0,1e12),settings)==(255,0,0)
    assert indicator_rgb(DiskRates("_total",1024,500),IndicatorSettings(saturation_kib=1,mix_colors=False))==(0,255,0)

def test_bad_settings():
    for invalid in (0,-1,float('nan'),float('inf')):
        with pytest.raises(ValueError): IndicatorSettings(saturation_kib=invalid).validate()
    with pytest.raises(ValueError): IndicatorSettings(device="").validate()

def test_missing_device_resets_baseline():
    ps=FakePs(); clock=iter([1,2]); sam=DiskActivitySampler(ps,lambda:next(clock))
    assert sam.sample("MISSING")==DiskRates("MISSING",0,0)
    assert sam.sample("MISSING")==DiskRates("MISSING",0,0)

def test_reset_clamped():
    ps=FakePs(); clock=iter([1,2]); sam=DiskActivitySampler(ps,lambda:next(clock))
    ps.n=3; sam.sample(); ps.n=1
    assert sam.sample().read_bps==0

def test_led_sampler_does_not_mutate_psutil():
    ps=FakePs(); sampler=DiskActivitySampler(ps,lambda:1.)
    sampler.devices();sampler.sample();assert ps.n==0

def test_runtime_integration_callback_with_ssd():
    from klrw.runtime import Monitor
    from klrw.model import Config
    from klrw.metrics import Sample
    from klrw.leds import PreviewBackend
    class BaseSampler:
        def sample(self): return Sample(0,0,0,0,0,0)
    class DiskSampler:
        def sample(self, device): return DiskRates(device, 1024, 0)
    data=[]
    mon=None
    def on_update(sample, states):
        data.append((dict(states),mon.disk_rates))
    mon=Monitor(Config(),on_update=on_update,sampler=BaseSampler(),backend=PreviewBackend(),disk_sampler=DiskSampler())
    mon.run(count=1)
    assert data[0][1]==DiskRates('_total',1024,0)
    assert mon.error is None


def test_runtime_disk_error_is_isolated():
    from klrw.runtime import Monitor
    from klrw.model import Config
    from klrw.metrics import Sample
    from klrw.leds import PreviewBackend
    class BaseSampler:
        def sample(self): return Sample(0,0,0,0,0,0)
    class BrokenDisk:
        def sample(self, device): raise OSError('fake disk unavailable')
    mon=Monitor(Config(),sampler=BaseSampler(),backend=PreviewBackend(),disk_sampler=BrokenDisk())
    mon.run(count=1)
    assert mon.error is None
    assert mon.disk_rates.read_bps==0
