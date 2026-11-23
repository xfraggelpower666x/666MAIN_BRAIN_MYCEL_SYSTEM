"""666TDI local daemon HTTP security/regression tests.

Tests use an ephemeral loopback port and a temporary evidence root; no Suno or
repository writes. Browser-specific acceptance remains a separate gate.
"""
from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from engine import daemon_cli, portable


class DaemonHttpGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.data_patch = patch.object(portable, "DATA", Path(self.temporary.name))
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), daemon_cli.Handler)
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.shutdown)
        self.port = self.server.server_port

    def request(self, method, path, *, host=None, origin=None, payload=None):
        headers = {"Host": host if host is not None else "127.0.0.1:%s" % self.port}
        if origin is not None:
            headers["Origin"] = origin
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        else:
            body = None
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        try:
            conn.request(method, path, body=body, headers=headers, skip_host=True)
            response = conn.getresponse()
            status = response.status
            raw = response.read()
            return status, json.loads(raw.decode("utf-8")) if response.getheader("Content-Type", "").startswith("application/json") else raw
        finally:
            conn.close()

    def example_feedback(self):
        return {"creator_confirmed": True, "track_id": "audit-track",
                "decision_id": "VOICE_LAYER_NEGOTIATION", "category": "VOICE",
                "rating": "SUCCESS", "intent_summary": "Clear vocal",
                "observed_outcome": "I heard intelligible words",
                "creator_note": "", "artifact_sha256": "", "device_route": "UNKNOWN"}

    def test_status_is_truthful_about_local_feedback_writes(self):
        status, body = self.request("GET", "/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(body["system_id"], "666TDI-001")
        self.assertFalse(body["read_only"])
        self.assertTrue(body["preanalysis_read_only"])
        self.assertTrue(body["feedback_writes_local"])
        self.assertFalse(body["global_learning"])

    def test_untrusted_host_cannot_read_ui(self):
        for host in ("evil.example:%s" % self.port,
                     "127.0.0.1:%s@evil.example" % self.port,
                     "127.0.0.1:9999"):
            with self.subTest(host=host):
                code, data = self.request("GET", "/", host=host)
                self.assertEqual(code, 403)
                self.assertEqual(data["error"], "HOST_NOT_ALLOWED")

    def test_untrusted_host_cannot_write_feedback(self):
        code, data = self.request("POST", "/api/feedback",
                                  host="evil.example:%s" % self.port,
                                  payload=self.example_feedback())
        self.assertEqual(code, 403)
        self.assertEqual(data["error"], "HOST_NOT_ALLOWED")
        self.assertFalse((Path(self.temporary.name) / "creator_evidence").exists())

    def test_cross_origin_post_rejected(self):
        code, data = self.request("POST", "/api/feedback",
                                  origin="https://external.example",
                                  payload=self.example_feedback())
        self.assertEqual(code, 403)
        self.assertEqual(data["error"], "ORIGIN_NOT_ALLOWED")

    def test_valid_local_feedback_and_readback(self):
        origin = "http://127.0.0.1:%s" % self.port
        code, receipt = self.request("POST", "/api/feedback",
                                     origin=origin, payload=self.example_feedback())
        self.assertEqual(code, 200)
        self.assertEqual(receipt["status"], "TRACK_LOCAL_CREATOR_EVIDENCE_RECORDED")
        code, result = self.request("POST", "/api/learning/read",
                                    origin=origin, payload={"track_id": "audit-track"})
        self.assertEqual(code, 200)
        self.assertEqual(result["observations"], 1)
        self.assertFalse(result["global_promotion"])

    def test_bad_feedback_enum_is_a_controlled_400(self):
        payload = {**self.example_feedback(), "category": []}
        code, result = self.request("POST", "/api/feedback", payload=payload)
        self.assertEqual(code, 400)
        self.assertEqual(result["error"], "INVALID_CATEGORY_OR_RATING")


if __name__ == "__main__":
    unittest.main()
