"""R11 stable Core Audio IMMDevice identity tests (mocked hardware backend)."""
import unittest
from unittest.mock import Mock, patch

from radiostreamer import capture
from radiostreamer.resin3 import windows_endpoints as ids
from radiostreamer.resin3.monitor_engine import LocalMonitor


class StableEndpointTests(unittest.TestCase):
    def setUp(self):
        self.a = ids.RenderEndpoint("{0.0.0.00000000}.{speaker-a}", "Speakers")
        self.b = ids.RenderEndpoint("{0.0.0.00000000}.{cable-b}", "CABLE Input")

    def fake_pa(self):
        sd = Mock()
        sd.query_hostapis.return_value = [{"name": "Windows WASAPI"}, {"name": "MME"}]
        sd.query_devices.return_value = [
            {"name": "Speakers", "hostapi": 0, "max_output_channels": 2},
            {"name": "CABLE Input", "hostapi": 0, "max_output_channels": 2},
            {"name": "Speakers", "hostapi": 1, "max_output_channels": 2},
        ]
        return sd

    def test_id_roundtrip(self):
        label = ids.stable_label(self.a)
        self.assertTrue(label.startswith("IMM:"))
        self.assertEqual(ids.parse_stable_label(label), self.a.endpoint_id)
        self.assertIsNone(ids.parse_stable_label("PA:4 | WASAPI | Speakers"))

    def test_id_cannot_be_replaced_by_new_endpoint_name(self):
        replaced = [ids.RenderEndpoint("{different}", "Speakers")]
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            ids.identity_by_id(replaced, self.a.endpoint_id)

    def test_duplicate_windows_names_fail_closed(self):
        duplicate = ids.RenderEndpoint("{different}", "Speakers")
        devices = [(8, "Speakers", "Windows WASAPI", "", 2)]
        self.assertIsNone(ids.unique_native_device_index(
            [self.a, duplicate], self.a.endpoint_id, devices, name_index=1, api_index=2))

    def test_portaudio_renumbering_still_resolves_imm_id(self):
        reordered = self.fake_pa()
        reordered.query_devices.return_value = [
            {"name": "CABLE Input", "hostapi": 0, "max_output_channels": 2},
            {"name": "Speakers", "hostapi": 0, "max_output_channels": 2},
        ]
        with patch.object(ids, "render_endpoints", return_value=[self.a, self.b]):
            self.assertEqual(LocalMonitor.resolve_output_device(
                reordered, ids.stable_label(self.a), 2), 1)

    def test_imm_monitor_does_not_select_mme_same_name(self):
        sd = self.fake_pa()
        with patch.object(ids, "render_endpoints", return_value=[self.a, self.b]):
            self.assertEqual(LocalMonitor.resolve_output_device(
                sd, ids.stable_label(self.a), 2), 0)

    def test_stale_imm_monitor_id_does_not_fallback_to_pa(self):
        sd = self.fake_pa()
        with patch.object(ids, "render_endpoints", return_value=[self.b]):
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                LocalMonitor.resolve_output_device(sd, ids.stable_label(self.a), 2)

    def test_imm_loopback_uses_selected_endpoint_after_reorder(self):
        backend = Mock()
        backend.get_loopback_device_info_generator.return_value = iter([
            {"index": 99, "name": "CABLE Input (loopback)"},
            {"index": 42, "name": "Speakers (loopback)"},
        ])
        with patch.object(ids, "render_endpoints", return_value=[self.a, self.b]):
            resolved = capture._resolve(backend, ids.stable_label(self.a))
        self.assertEqual(resolved["index"], 42)

    def test_ambiguous_loopback_name_rejected(self):
        backend = Mock()
        backend.get_loopback_device_info_generator.return_value = iter([
            {"index": 5, "name": "Speakers (loopback)"},
            {"index": 9, "name": "Speakers (loopback)"},
        ])
        with patch.object(ids, "render_endpoints", return_value=[self.a]):
            with self.assertRaisesRegex(OSError, "cannot be uniquely mapped"):
                capture._resolve(backend, ids.stable_label(self.a))

    def test_invalid_identity_label_rejected(self):
        with self.assertRaises(RuntimeError):
            ids.parse_stable_label("IMM:!!not-base64!! | Speakers")

    def test_unique_native_mapping_returns_none_for_other_api(self):
        records = [(3, "Speakers", "MME", "", 2)]
        self.assertIsNone(ids.unique_native_device_index(
            [self.a], self.a.endpoint_id, records, name_index=1, api_index=2))


if __name__ == "__main__":
    unittest.main()
