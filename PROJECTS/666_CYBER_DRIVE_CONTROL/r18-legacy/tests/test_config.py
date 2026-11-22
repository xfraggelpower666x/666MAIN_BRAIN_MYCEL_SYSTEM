import json
import pytest
from klrw.model import Config
from klrw.config import save,load
from klrw.cli import main

def test_roundtrip(tmp_path):
    f=tmp_path/'config.json'
    save(f,Config())
    assert load(f)==Config()

def test_no_implicit_hardware(tmp_path, capsys):
    f=tmp_path/'config.json'
    save(f,Config(hardware=True))
    assert main(['--config',str(f),'--count','1']) == 0
    assert '"leds"' in capsys.readouterr().out

def test_unknown_schema_and_keys(tmp_path):
    f=tmp_path/'config.json'
    f.write_text(json.dumps({"schema":2,"rules":[]}))
    with pytest.raises(ValueError):load(f)
    f.write_text(json.dumps({"schema":1,"unknown":1,"rules":[]}))
    with pytest.raises(ValueError):load(f)

def test_init_refuses_overwrite(tmp_path):
    f=tmp_path/'config.json'
    assert main(['--config',str(f),'--init-config'])==0
    with pytest.raises(SystemExit):main(['--config',str(f),'--init-config'])
