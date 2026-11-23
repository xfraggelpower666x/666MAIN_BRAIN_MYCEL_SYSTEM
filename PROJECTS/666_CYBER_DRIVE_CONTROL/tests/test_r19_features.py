"""R19 D/E tests against unchanged R18 source."""
import pytest
from klrw.bicolor_activity import CYAN, PINK, OFF
from r19_features import VisualBindings, VolumePulseMonitor

def test_visual_mapping_persist_and_evaluate(tmp_path):
    state=VisualBindings(tmp_path/"drive_workspace.json")
    assert all(x["mode"]=="off" for x in state.bindings.values())
    state.set_binding("caps","_total","read",4,{"_total"})
    loaded=VisualBindings(tmp_path/"drive_workspace.json")
    assert loaded.bindings["caps"]["mode"]=="read"
    assert loaded.preview({"_total":(6000,0)})["caps"] is True
    assert loaded.preview({"_total":(0,6000)})["caps"] is False
    assert loaded.preview({"_total":None})["caps"] is False

def test_invalid_mapping_does_not_change_disk(tmp_path):
    state=VisualBindings(tmp_path/"workspace.json")
    with pytest.raises(ValueError): state.set_binding("caps","missing","either",4,{"_total"})
    with pytest.raises(ValueError): state.set_binding("caps","_total","read",float("nan"),{"_total"})
    assert not state.path.exists()

def test_original_bicolor_pulse_and_hotplug_retirement():
    pulse=VolumePulseMonitor()
    s={"activity_threshold_bps":4096,"burst_bps":16384,"led_hold_ms":180,"led_quiet_ms":450}
    d={"id":"volume:usb","read_bps":60000,"write_bps":0}
    assert pulse.sample([d],0,s)["volume:usb"]==CYAN
    assert pulse.sample([d],100,s)["volume:usb"]==CYAN
    assert pulse.sample([d],181,s)["volume:usb"]==OFF
    d["write_bps"]=85000
    assert pulse.sample([d],500,s)["volume:usb"]==PINK
    assert pulse.sample([],800,s)=={}
    assert not pulse.engine.states
