import json
from types import SimpleNamespace
import pytest
from klrw.health import HealthHistory, HealthSnapshot, SmartctlReader, parse_smartctl
from klrw.overview import compose, clamp_percentage, colored_meter, OverviewSampler
from klrw.metrics import Sample
from klrw.ssd import DiskRates
from klrw.dashboard_cli import main


def test_smart_ok():
    s=parse_smartctl({"temperature":{"current":41},"smart_status":{"passed":True}},"ssd")
    assert s.available and s.passed and s.temperature_c == 41

def test_smart_failure():
    s=parse_smartctl({"smart_status":{"passed":False}},"ssd")
    assert s.available and s.passed is False

def test_smart_missing():
    assert parse_smartctl({}).available is False

def test_smart_invalid_temp():
    assert parse_smartctl({"temperature":{"current":300}}).temperature_c is None

def test_smart_nan():
    assert parse_smartctl({"temperature":{"current":float('nan')}}).temperature_c is None

def test_smart_warning():
    assert 'bad' in parse_smartctl({"messages":[{"severity":"warning","string":"bad"}]}).warning

def test_smart_invalid_document():
    with pytest.raises(ValueError):parse_smartctl([])

def test_smart_disabled():
    with pytest.raises(PermissionError):SmartctlReader().read("/dev/sda")

def test_smart_sanitize_device():
    with pytest.raises(ValueError):SmartctlReader(enabled=True,executable="smartctl").read("-x")

def test_smart_run_mock():
    calls=[]
    def run(argv,**kw):
        calls.append((argv,kw));return SimpleNamespace(stdout=json.dumps({"temperature":{"current":38}}),returncode=0)
    result=SmartctlReader(enabled=True,executable="smartctl",run=run).read("/dev/sda")
    assert result.temperature_c==38 and calls[0][0] == ['smartctl','-a','-j','/dev/sda'] and calls[0][1]['timeout']==8

def test_smart_invalid_json():
    with pytest.raises(RuntimeError):SmartctlReader(enabled=True,executable='s',run=lambda *a,**k:SimpleNamespace(stdout='no')).read('disk')

def test_smart_size_limit():
    with pytest.raises(ValueError):SmartctlReader(enabled=True,executable='s',run=lambda *a,**k:SimpleNamespace(stdout='x'*1048577)).read('disk')

def test_history_bounds():
    h=HealthHistory(2)
    for t in range(3):h.add(HealthSnapshot('sda',t,True,True),t)
    assert h.temperatures('sda') == ((1,1),(2,2))

def test_history_device():
    h=HealthHistory();h.add(HealthSnapshot('sda',30,True,True),0);h.add(HealthSnapshot('sdb',40,True,True),1)
    assert h.temperatures('sda')==((0,30),)

def test_bad_history():
    with pytest.raises(ValueError):HealthHistory(0)

def test_compose():
    s=compose(Sample(120,-3,-5,8,9,12),DiskRates('_total',34,12))
    assert s.cpu_pct==100 and s.memory_pct==0 and s.read_bps==0 and s.disk_read_bps==34

def test_overview_inject():
    class System:
        def sample(self):return Sample(33,22,1,2,3,4)
    class Disks:
        def sample(self,x):return DiskRates(x,5,6)
    s=OverviewSampler(System(),Disks(),'D:').sample()
    assert s.disk=='D:' and s.rx_bps==3

def test_meter():
    assert colored_meter(0,3)=='░░░' and colored_meter(100,3)=='███'

def test_meter_invalid():
    with pytest.raises(ValueError):colored_meter(1,0)

def test_clamp():
    assert clamp_percentage(-5)==0 and clamp_percentage(150)==100

def test_cli_snapshot(monkeypatch,capsys):
    class Fake:
        def __init__(self,device):pass
        def sample(self):return compose(Sample(10,20,0,0,0,0),DiskRates('_total',0,0))
    monkeypatch.setattr('klrw.dashboard_cli.OverviewSampler',Fake)
    assert main([])==0
    assert json.loads(capsys.readouterr().out)['overview']['cpu_pct']==10
