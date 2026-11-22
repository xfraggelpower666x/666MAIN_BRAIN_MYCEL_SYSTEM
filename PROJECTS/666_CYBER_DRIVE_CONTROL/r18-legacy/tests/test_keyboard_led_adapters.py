import pytest
from klrw.keyboard_led_adapters import UnsupportedHidBackend

def test_no_unverified_usb_hardware_write():
    backend=UnsupportedHidBackend()
    cap=backend.capabilities()
    assert not cap.verified and not cap.independent_of_lock_state
    with pytest.raises(RuntimeError):backend.set_led('caps',True)
