"""R10: deterministic device routing and relay-disconnect fault injection."""
import socket
import unittest
from unittest.mock import Mock, patch

from radiostreamer import capture
from radiostreamer.resin3.control_plane import RoutePlan
from radiostreamer.resin3.monitor_engine import LocalMonitor
from radiostreamer.resin3.relay_engine import RelayController
from radiostreamer.resin3.output_engine import OutputEngine


class DeviceRoutingTests(unittest.TestCase):
    def fake_sounddevice(self):
        sd = Mock()
        sd.query_hostapis.return_value = [{"name": "Windows WASAPI"}, {"name": "MME"}]
        sd.query_devices.return_value = [
            {"name": "Speakers", "hostapi": 0, "max_output_channels": 2},
            {"name": "Speakers", "hostapi": 1, "max_output_channels": 2},
            {"name": "CABLE Input", "hostapi": 0, "max_output_channels": 2},
            {"name": "Input only", "hostapi": 0, "max_output_channels": 0},
        ]
        return sd

    def test_duplicate_monitor_names_get_distinct_device_labels(self):
        sd = self.fake_sounddevice()
        labels = [item[3] for item in LocalMonitor._inventory(sd)]
        self.assertEqual(len(labels), 3)
        self.assertEqual(len(set(labels)), 3)
        self.assertEqual(LocalMonitor.resolve_output_device(sd, labels[1], 2), 1)

    def test_legacy_unique_monitor_name_is_supported(self):
        self.assertEqual(LocalMonitor.resolve_output_device(self.fake_sounddevice(), "CABLE Input", 2), 2)

    def test_duplicate_legacy_monitor_name_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "share this name"):
            LocalMonitor.resolve_output_device(self.fake_sounddevice(), "Speakers", 2)

    def test_stale_monitor_label_fails_instead_of_rerouting(self):
        sd = self.fake_sounddevice()
        with self.assertRaisesRegex(RuntimeError, "changed"):
            LocalMonitor.resolve_output_device(sd, "PA:0 | Windows WASAPI | CABLE Input", 2)

    def test_default_monitor_remains_available(self):
        self.assertIsNone(LocalMonitor.resolve_output_device(self.fake_sounddevice(), "Default output", 2))

    def test_explicit_wasapi_device_id_resolves_exactly(self):
        info = [{"index": 5, "name": "Speakers (loopback)"},
                {"index": 6, "name": "Speakers (loopback)"}]
        backend = Mock()
        backend.get_loopback_device_info_generator.return_value = iter(info)
        found = capture._resolve(backend, "WASAPI:6 | Speakers (loopback)")
        self.assertEqual(found["index"], 6)

    def test_legacy_ambiguous_wasapi_is_rejected(self):
        backend = Mock()
        backend.get_loopback_device_info_generator.return_value = iter([
            {"index": 5, "name": "Speakers (loopback)"},
            {"index": 6, "name": "Speakers (loopback)"},
        ])
        with self.assertRaisesRegex(OSError, "Multiple WASAPI endpoints"):
            capture._resolve(backend, "Speakers (loopback)")

    def test_stale_wasapi_id_cannot_fall_back(self):
        backend = Mock()
        backend.get_loopback_device_info_generator.return_value = iter([
            {"index": 5, "name": "Speakers (loopback)"}
        ])
        with self.assertRaisesRegex(OSError, "endpoint changed"):
            capture._resolve(backend, "WASAPI:6 | Speakers (loopback)")

    def test_virtual_cable_same_identity_feedback_blocked(self):
        with self.assertRaisesRegex(ValueError, "feedback loop"):
            RoutePlan.validate_monitor_route("device", "CABLE-A Output", "PA:4 | WASAPI | CABLE-A Input")

    def test_different_virtual_cables_are_not_confused(self):
        self.assertEqual(RoutePlan.validate_monitor_route(
            "device", "CABLE-A Output", "PA:3 | WASAPI | CABLE-B Input"), "")

    def test_wasapi_routing_warns_without_fake_identity_claim(self):
        self.assertIn("WASAPI", RoutePlan.validate_monitor_route(
            "loopback", "Default speakers", "Default output"))


class RelayFailureTests(unittest.TestCase):
    def make_controller(self, failures=0):
        output = Mock()
        return RelayController({"reconnect_delay": 1, "max_retries": failures}, output), output

    def test_real_socket_send_error_does_not_restart_encoder(self):
        controller, output = self.make_controller()
        encoder = Mock()
        sock = Mock()
        output.send.side_effect = BrokenPipeError("simulated connection loss")
        controller.attach(sock)
        controller.connected("local-radio")
        with self.assertRaises(BrokenPipeError):
            controller.send(b"encoded")
        had_sock, retry = controller.close("simulated connection loss")
        self.assertTrue(had_sock)
        self.assertEqual(retry[0], 1)
        self.assertGreater(controller.wait_remaining(), 0)
        encoder.stop.assert_not_called()
        output.close.assert_called_once_with(sock)

    def test_reconnect_receives_new_socket_after_disconnect(self):
        controller, output = self.make_controller()
        first, second = Mock(), Mock()
        controller.attach(first)
        controller.connected("local-radio")
        controller.close("disconnected")
        controller.attach(second)
        controller.connected("local-radio")
        self.assertIs(controller.current(), second)
        self.assertEqual(controller.policy.attempts, 0)
        self.assertEqual(controller.wait_remaining(), 0)
        self.assertEqual(controller.snapshot()["state"], "connected")

    def test_local_socket_failure_and_reconnect_without_provider(self):
        """Real OS sockets: simulate remote peer loss, then reconnect to a new local peer."""
        controller = RelayController({"reconnect_delay": 1, "max_retries": 0},
                                     OutputEngine({"server_type": "Icecast 2"}))
        left, right = socket.socketpair()
        try:
            controller.attach(left)
            controller.connected("local-pair")
            right.shutdown(socket.SHUT_RDWR)
            right.close()
            with self.assertRaises(OSError):
                controller.send(b"encoded" * 32)
            had_socket, result = controller.close("local peer dropped")
            self.assertTrue(had_socket)
            self.assertEqual(result[0], 1)
            self.assertGreater(controller.wait_remaining(), 0)
            left2, right2 = socket.socketpair()
            try:
                controller.attach(left2)
                controller.connected("local-pair")
                self.assertEqual(controller.send(b"resumed"), 7)
                self.assertEqual(right2.recv(7), b"resumed")
                self.assertEqual(controller.policy.attempts, 0)
                controller.close()
            finally:
                right2.close()
        finally:
            left.close()
            right.close()

    def test_configured_failure_limit_still_applies(self):
        controller, _ = self.make_controller(failures=2)
        self.assertEqual(controller.failed("first"), (1, 1, False))
        self.assertEqual(controller.failed("second"), (2, 2, True))


if __name__ == "__main__":
    unittest.main()
