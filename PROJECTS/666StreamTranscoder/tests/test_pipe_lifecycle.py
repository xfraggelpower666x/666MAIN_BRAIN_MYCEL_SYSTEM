"""R09 regression tests for FFmpeg process and pipe ownership."""
import io
import unittest
from unittest.mock import Mock

from radiostreamer.engine import PCMSource
from radiostreamer.resin3.encoder_engine import EncoderEngine


def terminated_process():
    proc = Mock()
    proc.poll.return_value = 0
    proc.stdin = io.BytesIO()
    proc.stdout = io.BytesIO()
    proc.stderr = io.BytesIO()
    return proc


class PipeLifecycleTests(unittest.TestCase):
    def test_pcm_source_closes_all_three_pipes(self):
        source = PCMSource(["ffmpeg"], 1024, False)
        process = terminated_process()
        source.proc = process
        source.close()
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)
        process.wait.assert_called_once()

    def test_pcm_source_close_is_idempotent(self):
        source = PCMSource(["ffmpeg"], 1024, True)
        source.proc = terminated_process()
        source.close()
        source.close()
        source.proc.wait.assert_called_once()

    def test_pcm_source_terminates_running_decoder(self):
        source = PCMSource(["ffmpeg"], 1024, False)
        source.proc = terminated_process()
        source.proc.poll.return_value = None
        source.close()
        source.proc.kill.assert_called_once()
        self.assertTrue(source.proc.stdout.closed)

    def test_encoder_closes_pipes_after_stop(self):
        host = Mock()
        host.encoder = terminated_process()
        adapter = EncoderEngine(host)
        adapter.stop()
        for pipe in (host.encoder.stdin, host.encoder.stdout, host.encoder.stderr):
            self.assertTrue(pipe.closed)
        host.encoder.wait.assert_called_once()

    def test_encoder_running_process_is_terminated(self):
        host = Mock()
        host.encoder = terminated_process()
        host.encoder.poll.return_value = None
        EncoderEngine(host).stop()
        host.encoder.kill.assert_called_once()


if __name__ == "__main__":
    unittest.main()
