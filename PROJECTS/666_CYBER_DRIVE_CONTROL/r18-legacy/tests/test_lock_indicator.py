import pytest
from klrw.lock_indicator import (parse_order, LockSnapshot, PreviewLockReader,
    LockIndicator, WindowsLockReader, display_text)

@pytest.mark.parametrize("s,expected", [("NCS", ("num", "caps", "scroll")), ("C", ("caps",)), ("", ())])
def test_order(s, expected):
    assert parse_order(s) == expected

@pytest.mark.parametrize("s", ["NN", "NCX", "NCSC", "n", "1", "CC", None])
def test_bad_order(s):
    with pytest.raises(ValueError):
        parse_order(s)

def test_only_changes_trigger():
    reader = PreviewLockReader()
    indicator = LockIndicator(reader, "NC")
    assert indicator.poll() == (("num", False), ("caps", False))
    assert indicator.poll() is None
    reader.snapshot = LockSnapshot(caps=True, num=False, scroll=False)
    assert indicator.poll() == (("num", False), ("caps", True))
    assert indicator.poll() is None

def test_hidden_changes_do_not_trigger():
    reader = PreviewLockReader()
    indicator = LockIndicator(reader, "N")
    indicator.poll()
    reader.snapshot = LockSnapshot(caps=True, num=False, scroll=True)
    assert indicator.poll() is None

def test_order_reconfiguration():
    i = LockIndicator(PreviewLockReader(caps=True), "N")
    i.poll()
    i.set_order("CN")
    assert i.poll() == (("caps", True), ("num", False))

def test_fake_win32_read_only():
    class User32:
        calls = []
        def GetKeyState(self, code):
            self.calls.append(code)
            return 1 if code == 0x14 else 0
    api = User32()
    assert WindowsLockReader(api).read() == LockSnapshot(True, False, False)
    assert len(api.calls) == 3

def test_display():
    assert display_text((("caps", True), ("num", False))) == "C ●   N ○"
    assert display_text(()) == "Keine Lock-Anzeigen"

def test_snapshot_mapping():
    assert LockSnapshot(True, False, True).as_dict() == {"caps":True,"num":False,"scroll":True}
