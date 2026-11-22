"""R19 bridge contracts: no fake logical-volume attribution or device writes."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

FILE = Path(__file__).resolve().parents[1] / "r19-electron" / "bridge" / "volume_metrics.py"
spec = importlib.util.spec_from_file_location("volume_metrics", FILE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def test_unavailable_is_explicit():
    d = SimpleNamespace(key="volume:abc", mount="C:", label="System", filesystem="NTFS", removable=False)
    ws = SimpleNamespace(
        preferences=lambda _: {"tray": True, "overlay": True, "keyboard": False},
        data={"activity_threshold_bps": 4096, "led_hold_ms": 180, "led_quiet_ms": 450,
              "overlay": {"layout": "minimal"}},
    )
    snap = bridge.snapshot(ws, lambda: [d], None, timestamp="test")
    assert snap["protocol"] == "cyber-drive.metrics.v2"
    assert snap["volumes"][0]["measurement"] == "unavailable"
    assert snap["volumes"][0]["write_bps"] is None
    assert snap["volumes"][0]["targets"]["keyboard"] is False


def test_pdh_letter_and_identity_preserved():
    d = SimpleNamespace(key="volume:unique-usb", mount="G:", label="Ventoy", filesystem="exFAT", removable=True)
    ws = SimpleNamespace(
        preferences=lambda _: {"tray": False, "overlay": True, "keyboard": False},
        data={"activity_threshold_bps": 4096, "led_hold_ms": 180, "led_quiet_ms": 450,
              "overlay": {"layout": "horizontal"}},
    )
    class Sampler:
        configured = None
        def configure(self, letters): self.configured = letters
        def sample_all(self): return {"G:": SimpleNamespace(read_bps=1200, write_bps=4300)}
    sampler = Sampler()
    snap = bridge.snapshot(ws, lambda: [d], sampler, timestamp="test")
    assert sampler.configured == {"G:"}
    assert snap["volumes"][0]["id"] == "volume:unique-usb"
    assert snap["volumes"][0]["read_bps"] == 1200
    assert snap["volumes"][0]["write_bps"] == 4300
    assert snap["volumes"][0]["measurement"] == "logical_pdh"


def test_invalid_rates_never_become_activity():
    assert bridge.normalize_rates(SimpleNamespace(read_bps=float("nan"), write_bps=-3)) == (None, None)
