import pytest
from klrw.activity_presenter import activity_visual, summarize_devices, activity_frame
from klrw.activity_window import formatted_bps
from klrw.driver_diagnostics import driver_monitor_status

def test_idle():
    x=activity_visual(0,0)
    assert (x.status,x.hex_color)==("idle","#000000")

def test_read():
    x=activity_visual(1024,0,saturation_kib=1)
    assert (x.status,x.hex_color)==("read","#00ff00")

def test_write():
    x=activity_visual(0,1024,saturation_kib=1)
    assert (x.status,x.hex_color)==("write","#ff0000")

def test_mix():
    assert activity_visual(1024,1024,1).hex_color=="#ffff00"

def test_clamped():
    assert activity_visual(10000000,0,1).read_level==255

def test_bad():
    for x in (-1,float('nan'),float('inf'),True):
        with pytest.raises(ValueError): activity_visual(x,0)

def test_bad_saturation():
    with pytest.raises(ValueError):activity_visual(0,0,0)

def test_devices():
    assert summarize_devices({'_total':(500,500),'d1':(5,7),'d2':(3,4)})==(8,11)

def test_devices_bad():
    with pytest.raises(ValueError):summarize_devices({'d1':(-2,1)})

def test_frames():
    assert activity_frame(1024,0,0,1)=='#00ff00'
    assert activity_frame(1024,0,1,1)=='#009900'

def test_bad_phase():
    with pytest.raises(ValueError):activity_frame(0,0,2)

def test_format():
    assert formatted_bps(1024)=='1.0 KiB/s'
    assert formatted_bps(1048576)=='1.0 MiB/s'

def test_diagnostic_disabled():
    d=driver_monitor_status()
    assert not d.available and 'opt-in' in d.reason
