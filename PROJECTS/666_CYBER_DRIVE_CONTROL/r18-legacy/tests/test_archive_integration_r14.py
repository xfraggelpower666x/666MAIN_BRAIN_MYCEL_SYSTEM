import json
from types import SimpleNamespace
import pytest
from klrw.drive_workspace import Workspace
from klrw.drive_speed_display import format_speed, describe_rate, active_channels
from klrw.ssd import DiskRates


def test_speed_units_read_write():
    rate=DiskRates('C:',1024*1024,2048)
    assert '1.00 MiB/s' in describe_rate(rate,{'speed_unit':'MiB/s','speed_decimals':2})
    assert '0.00 MiB/s' in describe_rate(rate,{'speed_unit':'MiB/s','speed_decimals':2})
    assert 'R 1024.0 / W 2.0 KiB/s'==describe_rate(rate,{'speed_unit':'KiB/s','speed_decimals':1},compact=True)
    assert format_speed(125,'bit/s',0)=='1000 bit/s'


def test_activity_threshold():
    rate=DiskRates('E:',4096,8192)
    assert active_channels(rate,4096)==(False,True)
    assert active_channels(None)==(False,False)
    with pytest.raises(ValueError):active_channels(rate,-1)


def test_persistent_display_preferences(tmp_path):
    target=tmp_path/'config.json';s=Workspace(target)
    s.data.update(speed_unit='MB/s',speed_decimals=3,display_mode='compact',activity_threshold_bps=16*1024)
    s.save();r=Workspace(target)
    assert (r.data['speed_unit'],r.data['speed_decimals'],r.data['display_mode'],r.data['activity_threshold_bps'])==('MB/s',3,'compact',16*1024)


def test_invalid_display_configuration_rejected(tmp_path):
    target=tmp_path/'config.json'
    target.write_text(json.dumps({'schema':1,'speed_unit':'unexpected','speed_decimals':99,'display_mode':'invalid','activity_threshold_bps':-9}))
    s=Workspace(target)
    assert s.data['speed_unit']=='KiB/s' and s.data['speed_decimals']==1
    assert s.data['display_mode']=='detailed' and s.data['activity_threshold_bps']==4096


def test_pdh_hotplug_source_contract():
    from pathlib import Path
    src=(Path(__file__).parents[1]/'src/klrw/windows_logical_io.py').read_text()
    assert 'PdhRemoveCounter' in src
    assert 'if letter not in wanted' in src


def test_no_foreign_runtime_dependencies():
    from pathlib import Path
    root=Path(__file__).parents[1]
    p=(root/'pyproject.toml').read_text()
    assert 'gpiozero' not in p and 'System.Management' not in p
    assert len(list(root.rglob('*.bat')))==1


def test_pdh_replug_recreates_handles():
    import ctypes
    from klrw.windows_logical_io import WindowsLogicalDiskSampler
    class Fn:
        def __init__(self, callback): self.callback=callback
        def __call__(self,*args):return self.callback(*args)
    class Pdh:
        def __init__(self):
            self.added=[];self.removed=[];self.next=10
            self.PdhOpenQueryW=Fn(lambda name,data,target: 0)
            self.PdhAddEnglishCounterW=Fn(self._add)
            self.PdhRemoveCounter=Fn(lambda handle:self.removed.append(handle.value) or 0)
            self.PdhCollectQueryData=Fn(lambda query:0)
            self.PdhGetFormattedCounterValue=Fn(lambda *args:0)
            self.PdhCloseQuery=Fn(lambda query:0)
        def _add(self,query,path,userdata,target):
            self.next+=1
            ctypes.cast(target,ctypes.POINTER(ctypes.c_void_p)).contents.value=self.next
            self.added.append((path,self.next));return 0
    mock=Pdh();sampler=WindowsLogicalDiskSampler(mock)
    sampler.configure(['C:','E:'])
    assert set(sampler.counters)=={'C:','E:'}
    old_e=tuple(handle.value for handle in sampler.counters['E:'])
    sampler.configure(['C:'])
    assert set(sampler.counters)=={'C:'}
    assert set(old_e)<=set(mock.removed)
    sampler.configure(['C:','E:'])
    assert tuple(handle.value for handle in sampler.counters['E:'])!=old_e
    sampler.close()
