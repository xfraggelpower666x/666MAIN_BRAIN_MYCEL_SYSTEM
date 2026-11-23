import unittest

from radiostreamer.resin3.control_plane import (
    ConnectionWatch, GainStage, ReconnectPolicy, RoutePlan, peak_dbfs,
)
from radiostreamer.resin3.relay_engine import RelayController


class Resin3ControlPlaneTests(unittest.TestCase):
    def test_stream_gain_is_independent_and_clamped(self):
        pcm = (10000).to_bytes(2, "little", signed=True) * 4
        stage = GainStage(50)
        self.assertEqual(int.from_bytes(stage.process(pcm)[:2], "little", signed=True), 5000)
        stage.set_percent(250)
        self.assertEqual(int.from_bytes(stage.process(pcm)[:2], "little", signed=True), 20000)
        stage.set_percent(0)
        self.assertEqual(stage.process(pcm), bytes(len(pcm)))

    def test_peak_meter_reports_dbfs(self):
        silence = bytes(16)
        full = (-32768).to_bytes(2, "little", signed=True) * 4
        self.assertEqual(peak_dbfs(silence), -120.0)
        self.assertAlmostEqual(peak_dbfs(full), 0.0, places=5)

    def test_route_plan_identifies_wasapi_virtual_input_and_outputs(self):
        route = RoutePlan.describe("loopback", "Icecast 2", "CABLE Input")
        self.assertIn("WASAPI", route["input"])
        self.assertIn("Icecast", route["output"])
        self.assertEqual(route["monitor"], "CABLE Input")
        self.assertIn("virtual cable", RoutePlan.describe("device", "Shoutcast v1")["input"])

    def test_reconnect_policy_backs_off_and_resets(self):
        policy = ReconnectPolicy(base_delay=3, max_retries=3, cap=10)
        self.assertEqual(policy.failed(), (1, 3, False))
        self.assertEqual(policy.failed(), (2, 6, False))
        self.assertEqual(policy.failed(), (3, 10, True))
        policy.connected()
        self.assertEqual(policy.failed(), (1, 3, False))

    def test_connection_watch_tracks_activity(self):
        watch = ConnectionWatch()
        watch.connecting("radio.example:8001")
        self.assertEqual(watch.snapshot()["state"], "connecting")
        watch.connected("radio.example:8001")
        watch.sent(1024)
        snap = watch.snapshot()
        self.assertEqual(snap["state"], "connected")
        self.assertEqual(snap["bytes_sent"], 1024)
        watch.disconnected("socket closed")
        self.assertEqual(watch.snapshot()["state"], "retrying")

    def test_relay_controller_applies_backoff_after_socket_loss(self):
        class DummyOutput:
            def open(self):
                return object()
        relay = RelayController({"reconnect_delay": 2, "max_retries": 3}, DummyOutput())
        relay.connecting("radio.example:8001")
        relay.connected("radio.example:8001")
        attempts, delay, exhausted = relay.disconnected("send failed")
        self.assertEqual((attempts, delay, exhausted), (1, 2, False))
        self.assertGreater(relay.wait_remaining(), 0)

    def test_relay_controller_stops_after_configured_failures(self):
        class DummyOutput:
            def open(self):
                return object()
        relay = RelayController({"reconnect_delay": 1, "max_retries": 2}, DummyOutput())
        self.assertEqual(relay.failed("connect failed"), (1, 1, False))
        self.assertEqual(relay.failed("connect failed again"), (2, 2, True))


if __name__ == "__main__":
    unittest.main()
