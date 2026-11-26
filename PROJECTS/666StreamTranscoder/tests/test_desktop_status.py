import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from radiostreamer.resin3 import desktop_status as d

class TestDesktopStatus(unittest.TestCase):
    def test_disconnected(self):
        x = d.sanitized_snapshot(status="live", input_dbfs=math.nan)
        self.assertEqual(x["status"], "off")
        self.assertFalse(x["on_air"])
        self.assertIsNone(x["input_dbfs"])
    def test_allowlist(self):
        class Bus:
            def snapshot(self):
                return {"source": type("Event", (), {"state":"active"})(), "secret": "DO_NOT_EXPOSE"}
        class Broadcaster:
            live = True
            password = "SECRET_PASSWORD"
            status_bus = Bus()
        x = d.sanitized_snapshot(status="live", broadcaster=Broadcaster(), output_dbfs=-5.55, timestamp=42)
        self.assertTrue(x["on_air"])
        self.assertEqual(x["components"]["source"], "active")
        self.assertNotIn("secret", json.dumps(x).lower())
        self.assertEqual(x["timestamp_ms"], 42000)
    def test_atomic_owner_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "desktop-status-v1.json"
            with patch.object(d, "DATA_DIR", Path(tmp)), patch.object(d, "STATUS_FILE", path):
                d.write_desktop_status(status="off", timestamp=42)
                self.assertEqual(json.loads(path.read_text())["timestamp_ms"], 42000)
                d.remove_desktop_status()
                self.assertFalse(path.exists())
    def test_foreign_pid_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "desktop-status-v1.json"
            path.write_text('{"pid":9999999}')
            with patch.object(d, "STATUS_FILE", path):
                d.remove_desktop_status()
                self.assertTrue(path.exists())
