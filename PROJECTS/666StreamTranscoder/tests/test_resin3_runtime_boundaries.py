"""R06: Resin 3 runtime boundary acceptance with mocked external I/O.

These tests do not claim Windows device, FFmpeg, or provider-side acceptance.
They exercise the actual adapters and preserved Broadcaster signal handoff.
"""
import unittest
from unittest.mock import Mock, patch

from radiostreamer.engine import Broadcaster
from radiostreamer.resin3.control_plane import GainStage
from radiostreamer.resin3.input_router import InputRouter
from radiostreamer.resin3.encoder_engine import EncoderEngine
from radiostreamer.resin3.output_engine import OutputEngine
from radiostreamer.resin3.relay_engine import RelayController


class RuntimeBoundaryTests(unittest.TestCase):
    def test_input_device_uses_existing_pcm_source(self):
        host = Mock()
        host.cfg = {"source": "device", "device": "CABLE Output"}
        host.chunk_bytes = 2048
        host._decoder_cmd.return_value = ["ffmpeg", "capture"]
        # InputRouter imports the preserved PCMSource lazily from radiostreamer.engine.
        with patch("radiostreamer.engine.PCMSource") as source_type, \
             patch("radiostreamer.resin3.input_router.tools.device_input_args",
                   return_value=["-f", "dshow", "-i", "audio=CABLE Output"]):
            source = InputRouter(host).open_live()
        self.assertIs(source, source_type.return_value)
        source.start.assert_called_once()
        self.assertEqual(source_type.call_args.args[1], 2048)
        self.assertTrue(source_type.call_args.args[2])

    def test_wasapi_capture_remains_original_3dx_primitive(self):
        host = Mock()
        host.cfg = {"source": "loopback", "loopback_device": ""}
        host.ffmpeg = "ffmpeg"
        host.sr = 44100
        host.ch = 2
        host.chunk_bytes = 8820
        capture = Mock(rate=48000, channels=2, name="System loopback")
        with patch("radiostreamer.resin3.input_router.create_capture", return_value=capture), \
             patch("radiostreamer.engine.PCMSource") as source_type:
            InputRouter(host).open_live()
        args = source_type.call_args
        self.assertIs(args.kwargs["feeder"], capture)
        self.assertIn("pipe:0", args.args[0])
        source_type.return_value.start.assert_called_once()

    def test_relay_input_decodes_to_existing_pcm_source(self):
        host = Mock()
        host.cfg = {"source": "relay", "relay_url": "https://example.org/live"}
        host.chunk_bytes = 4096
        host._decoder_cmd.return_value = ["ffmpeg", "-i", "https://example.org/live"]
        with patch("radiostreamer.engine.PCMSource") as source_type:
            InputRouter(host).open_live()
        self.assertTrue(source_type.call_args.args[2])
        source_type.return_value.start.assert_called_once()

    def test_encoder_lifecycle_uses_one_persistent_process(self):
        host = Mock()
        host.ffmpeg, host.sr, host.ch = "ffmpeg", 44100, 2
        host.cfg = {"bitrate": 128}
        process = Mock()
        with patch("radiostreamer.resin3.encoder_engine.mp3_command",
                   return_value=["ffmpeg", "-f", "mp3"]) as command, \
             patch("radiostreamer.resin3.encoder_engine.tools.popen",
                   return_value=process) as popen, \
             patch("radiostreamer.resin3.encoder_engine.threading.Thread") as thread:
            returned = EncoderEngine(host).start()
        self.assertIs(returned, process)
        self.assertIs(host.encoder, process)
        command.assert_called_once()
        popen.assert_called_once()
        self.assertEqual(thread.call_count, 2)

    def test_output_delegates_existing_protocol_and_sends_bytes(self):
        cfg = {"server_type": "Icecast 2"}
        sock = Mock()
        with patch("radiostreamer.resin3.output_engine.connect", return_value=sock) as connect:
            output = OutputEngine(cfg)
            self.assertIs(output.open(), sock)
            connect.assert_called_once_with(cfg)
        self.assertEqual(OutputEngine.send(sock, b"encoded"), 7)
        sock.sendall.assert_called_once_with(b"encoded")
        OutputEngine.close(sock)
        sock.close.assert_called_once()

    def test_relay_controller_owns_connection_and_reconnect(self):
        socket = Mock()
        output = Mock()
        output.open.return_value = socket
        output.send.return_value = 4
        ctrl = RelayController({"reconnect_delay": 1, "max_retries": 0}, output)
        self.assertIs(ctrl.open(), socket)
        ctrl.attach(socket)
        ctrl.connected("radio.example:8001")
        self.assertEqual(ctrl.send(b"data"), 4)
        self.assertEqual(ctrl.snapshot()["bytes_sent"], 4)
        had_socket, retry = ctrl.close("socket failed")
        self.assertTrue(had_socket)
        self.assertEqual(retry[0], 1)
        self.assertGreater(ctrl.wait_remaining(), 0)
        self.assertIsNone(ctrl.current())
        output.close.assert_called_once_with(socket)

    def test_stream_gain_does_not_change_monitor_audio(self):
        host = object.__new__(Broadcaster)
        host.cfg = {"mic_device": "", "mic_duck": 30}
        host.mic_on = False
        host.mic_src = None
        host.music_gain = 1.0
        host.monitor_sink = Mock()
        host.stream_gain = GainStage(50)
        host.emit = Mock()
        original = (10000).to_bytes(2, "little", signed=True) * 8
        transmitted = host._with_mic(original)
        self.assertEqual(host.monitor_sink.write.call_args.args[0], original)
        self.assertEqual(int.from_bytes(transmitted[:2], "little", signed=True), 5000)
        event = [call for call in host.emit.call_args_list if call.args[0] == "meters"]
        self.assertEqual(len(event), 1)
        self.assertGreater(event[0].args[1][0], event[0].args[1][1])

    def test_virtual_cable_feedback_route_is_blocked(self):
        from radiostreamer.resin3.control_plane import RoutePlan
        with self.assertRaisesRegex(ValueError, "feedback loop"):
            RoutePlan.validate_monitor_route("device", "CABLE Output (VB-Audio)", "CABLE Input (VB-Audio)")

    def test_physical_monitor_output_is_allowed(self):
        from radiostreamer.resin3.control_plane import RoutePlan
        self.assertEqual(RoutePlan.validate_monitor_route("device", "CABLE Output", "Speakers"), "")

    def test_monitor_stop_never_disposes_broadcast_engine(self):
        from radiostreamer.resin3.relay_engine import RelaySession
        broadcaster = Mock(sr=44100, ch=2)
        monitor = Mock()
        session = RelaySession(broadcaster, monitor=monitor)
        session.stop_monitor()
        monitor.stop.assert_called_once()
        broadcaster.stop.assert_not_called()


if __name__ == "__main__":
    unittest.main()
