import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


NODE_PATH = Path(__file__).resolve().parents[1] / "nodes.py"
package = types.ModuleType("ace_step_test_package")
package.__path__ = [str(NODE_PATH.parent)]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location("ace_step_test_package.nodes", NODE_PATH)
nodes = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"numpy": types.ModuleType("numpy"),
                              "torch": types.ModuleType("torch"),
                              "requests": types.ModuleType("requests")}):
    spec.loader.exec_module(nodes)


class RequestAudioRoleTests(unittest.TestCase):
    def build(self, **params):
        with patch.object(nodes, "_encode_audio_b64", side_effect=lambda audio: audio):
            return nodes._build_request_body(params, {})

    def audio(self, body):
        content = body["messages"][0]["content"]
        return [part["input_audio"]["data"] for part in content if part["type"] == "input_audio"]

    def test_cover_orders_source_before_reference(self):
        body = self.build(task_type="cover", src_audio="source", refer_audio="reference")
        self.assertEqual(self.audio(body), ["source", "reference"])

    def test_source_converts_text_to_cover_and_stays_first(self):
        body = self.build(src_audio="source", refer_audio="reference")
        self.assertEqual(body["task_type"], "cover")
        self.assertEqual(self.audio(body), ["source", "reference"])

    def test_text_to_music_keeps_reference_audio(self):
        body = self.build(refer_audio="reference")
        self.assertEqual(body["task_type"], "text2music")
        self.assertEqual(self.audio(body), ["reference"])

    def test_repaint_rejects_ambiguous_reference_without_source(self):
        with self.assertRaisesRegex(RuntimeError, "requires source audio"):
            self.build(task_type="repaint", refer_audio="reference")

    def test_cover_with_codes_only_remains_supported(self):
        body = self.build(task_type="cover", audio_codes="codes")
        self.assertEqual(body["task_type"], "cover")
        self.assertEqual(body["audio_codes"], "codes")


if __name__ == "__main__":
    unittest.main()
