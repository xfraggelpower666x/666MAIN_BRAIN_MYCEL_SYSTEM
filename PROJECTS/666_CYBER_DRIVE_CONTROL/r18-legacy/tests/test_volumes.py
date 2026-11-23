"""Synthetic capacity tests; safe on all OS, no drive writes."""
from types import SimpleNamespace as N
import json
import pytest
from klrw.volumes import VolumeSampler, Volume, severity, compact_free_gib
from klrw import capacity_cli

@pytest.mark.parametrize("percent,result",[(0,"ok"),(79.9,"ok"),(80,"warning"),(94.9,"warning"),(95,"critical"),(100,"critical")])
def test_severity(percent,result): assert severity(percent)==result

@pytest.mark.parametrize("inputs",[(float("nan"),80,95),(1,80,80),(1,99,90),(-1,80,95),(101,80,95),(0,-1,95),(0,0,101)])
def test_invalid(inputs):
    with pytest.raises(ValueError): severity(*inputs)

class Fake:
    def disk_partitions(self,all=False):
        return [N(mountpoint="C:\\",device="C:",fstype="NTFS"),N(mountpoint="D:\\",device="D:",fstype="NTFS"),N(mountpoint="C:\\",device="C:",fstype="NTFS"),N(mountpoint="Z:\\",device="\\\\server\\share",fstype="cifs")]
    def disk_usage(self,path):
        if path=="D:\\": raise PermissionError("denied")
        return N(total=1000,used=810,free=190,percent=81)

def test_sample_missing_and_duplicate():
    volumes, errors=VolumeSampler(ps=Fake()).sample()
    assert len(volumes)==1 and volumes[0].mountpoint=="C:\\"
    assert volumes[0].used_percent==81.0 and volumes[0].status=="warning"
    assert errors=={"D:\\":"PermissionError"}

def test_remote_optin():
    volumes, errors=VolumeSampler(ps=Fake(),include_remote=True).sample()
    assert {v.mountpoint for v in volumes}=={"C:\\","Z:\\"}

def test_unit_conversion():
    obj=N(free_bytes=2*1024**3)
    assert compact_free_gib(obj)==2.0

def test_cli_json(capsys,monkeypatch):
    monkeypatch.setattr(capacity_cli,"VolumeSampler",lambda **kwargs: N(sample=lambda:([Volume(mountpoint="X:",device="x",filesystem="NTFS",total_bytes=100,used_bytes=50,free_bytes=50,used_percent=50.,status="ok")],{})))
    assert capacity_cli.main(["--json"])==0
    assert json.loads(capsys.readouterr().out)["volumes"][0]["status"]=="ok"
