import unittest

from radiostreamer.resin3.status_bus import StatusBus
from radiostreamer.resin3.source_stream import stream_input_args
from radiostreamer.resin3.encoder import mp3_command


class Resin3ModuleTests(unittest.TestCase):
    def test_status_bus_publishes_and_snapshots(self):
        bus = StatusBus()
        received = []
        unsubscribe = bus.subscribe(received.append)
        event = bus.publish("relay", "connected", "test")
        self.assertEqual(received, [event])
        self.assertEqual(bus.snapshot()["relay"].state, "connected")
        unsubscribe()
        bus.publish("relay", "disconnected")
        self.assertEqual(len(received), 1)

    def test_stream_adapter_rejects_non_http_urls(self):
        with self.assertRaises(ValueError):
            stream_input_args("not-a-stream-url")

    def test_stream_adapter_accepts_http_url(self):
        args = stream_input_args("https://example.invalid/radio.mp3")
        self.assertIn("-i", args)

    def test_encoder_builder_preserves_selected_output_format(self):
        cmd = mp3_command("ffmpeg", 44100, 2, 192)
        self.assertIn("libmp3lame", cmd)
        self.assertIn("192k", cmd)
        self.assertEqual(cmd[-2:], ["mp3", "pipe:1"])


if __name__ == "__main__":
    unittest.main()
