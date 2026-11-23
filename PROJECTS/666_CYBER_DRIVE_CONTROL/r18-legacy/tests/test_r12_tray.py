import pytest
from klrw.tray_state import make_frame, ChangeGate, TrayFrame
from klrw.lock_indicator import LockSnapshot

@pytest.mark.parametrize("snapshot,expected",[
    (LockSnapshot(False,False,False),(False,False,False)),
    (LockSnapshot(True,False,False),(False,True,False)),
    (LockSnapshot(False,True,False),(True,False,False)),
    (LockSnapshot(False,False,True),(False,False,True)),
    (LockSnapshot(True,True,True),(True,True,True)),
])
def test_states(snapshot,expected):
    assert make_frame(snapshot).enabled == expected

def test_order():
    assert make_frame(LockSnapshot(True,False,True),"SC").enabled == (True,True)

def test_hidden():
    assert make_frame(LockSnapshot(True,True,True),"").label == "No indicators selected"

def test_invalid_order():
    with pytest.raises(ValueError): make_frame(LockSnapshot(False,False,False),"NN")

def test_wrong_snapshot():
    with pytest.raises(TypeError): make_frame({"caps":True})

def test_change_gate():
    gate=ChangeGate()
    a=make_frame(LockSnapshot(False,False,False))
    b=make_frame(LockSnapshot(False,True,False))
    assert gate.accept(a) is True
    assert gate.accept(a) is False
    assert gate.accept(b) is True

def test_gate_tracks_order():
    gate=ChangeGate()
    s=LockSnapshot(False,False,False)
    assert gate.accept(make_frame(s,"NCS"))
    assert gate.accept(make_frame(s,"CNS"))

def test_gate_wrong_type():
    with pytest.raises(TypeError):ChangeGate().accept(None)

def test_frame_immutable():
    a=make_frame(LockSnapshot(False,False,False))
    with pytest.raises(Exception): a.label="other"

def test_preview_draw_icon():
    pillow=pytest.importorskip('PIL')
    from klrw.tray_window import draw_icon
    im=draw_icon(make_frame(LockSnapshot(True,False,True)))
    assert im.size==(64,64)
    assert im.mode=='RGBA'

def test_invalid_icon_size():
    pytest.importorskip('PIL')
    from klrw.tray_window import draw_icon
    with pytest.raises(ValueError):draw_icon(make_frame(LockSnapshot(False,False,False)),8)

def test_interval_validation():
    import inspect
    from klrw.tray_window import TrayWindow
    assert 'interval_ms' in inspect.signature(TrayWindow).parameters
