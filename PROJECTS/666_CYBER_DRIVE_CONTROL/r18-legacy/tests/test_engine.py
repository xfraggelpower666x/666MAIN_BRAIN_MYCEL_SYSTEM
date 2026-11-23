from klrw.engine import RuleEngine
from klrw.model import Config, Rule
from klrw.metrics import Sample
from klrw.leds import PreviewBackend

def s(cpu=0, memory=0, disk_read=0, disk_write=0, network_rx=0, network_tx=0):
    return Sample(cpu, memory, disk_read, disk_write, network_rx, network_tx)

def test_defaults_simulated():
    c = Config()
    assert not c.hardware
    backend = PreviewBackend()
    engine = RuleEngine(c, backend)
    assert engine.tick(s(cpu=80, disk_write=5000, network_rx=6000)) == {"caps":True,"num":True,"scroll":True}
    assert engine.tick(s()) == {"caps":False,"num":False,"scroll":False}
    engine.close()

def test_or_rules_and_edges():
    cfg = Config(rules=(Rule("cpu","caps",50),Rule("memory","caps",60)))
    backend = PreviewBackend()
    engine = RuleEngine(cfg, backend)
    assert engine.tick(s(cpu=50))["caps"]
    assert engine.tick(s(memory=60))["caps"]
    assert not engine.tick(s())["caps"]

def test_threshold_validation():
    import pytest
    with pytest.raises(ValueError): Config(rules=(Rule("cpu","caps",110),)).validate()
    with pytest.raises(ValueError): Config(interval=0.01).validate()
    with pytest.raises(ValueError): Config(rules=(Rule("invalid","caps",2),)).validate()

def test_cleanup():
    backend = PreviewBackend()
    engine = RuleEngine(Config(), backend)
    engine.tick(s(cpu=95))
    engine.close()
    assert not any(backend.states.values())
