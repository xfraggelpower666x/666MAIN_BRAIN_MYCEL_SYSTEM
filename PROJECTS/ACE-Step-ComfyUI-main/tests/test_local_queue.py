import importlib.util
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "local_queue", Path(__file__).resolve().parents[1] / "local_queue.py"
)
local_queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_queue)


class Response:
    def __init__(self, data=None, content=b"wave"):
        self.data = data
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"code": 200, "data": self.data, "error": None}


class Http:
    def __init__(self, entries):
        self.entries = iter(entries)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if url.endswith("/release_task"):
            return Response({"task_id": "id"})
        return Response([{"task_id": "id", **next(self.entries)}])

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response()


class LocalQueueTests(unittest.TestCase):
    def test_server_mode_requires_cloud_consent_and_forces_local_endpoint(self):
        self.assertEqual(
            local_queue.resolve_api_url("local", "https://remote.example", False),
            "http://127.0.0.1:8002",
        )
        with self.assertRaisesRegex(ValueError, "explicit consent"):
            local_queue.resolve_api_url("cloud", "https://api.acemusic.ai", False)
        self.assertEqual(
            local_queue.resolve_api_url("cloud", "", True),
            "https://api.acemusic.ai",
        )
        self.assertEqual(
            local_queue.resolve_api_url("cloud", "https://music.example/api", True),
            "https://music.example/api",
        )
        for url in ("http://music.example", "https://user:pass@music.example", "ftp://music.example"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                local_queue.resolve_api_url("cloud", url, True)

    def test_local_api_key_is_separate_from_remote_cloud_credentials(self):
        with patch.dict(os.environ, {"ACESTEP_API_KEY": "cloud-secret"}, clear=True):
            headers = local_queue.local_api_headers()
            self.assertNotIn("Authorization", headers)
            self.assertNotIn("Content-Type", headers)
            self.assertEqual(local_queue.local_api_headers(json_body=True)["Content-Type"], "application/json")
        with patch.dict(os.environ, {
            "ACESTEP_API_KEY": "cloud-secret",
            "ACESTEP_LOCAL_API_KEY": "local-secret",
        }, clear=True):
            self.assertEqual(
                local_queue.local_api_headers()["Authorization"],
                "Bearer local-secret",
            )

    def test_text_to_music_polls_and_fetches_only_the_local_audio_route(self):
        http = Http([
            {"status": 0, "result": "[]"},
            {"status": 1, "result": json.dumps([{"file": "/v1/audio?path=C%3A%5Coutput%5Csong.wav"}])},
        ])
        audio, info = local_queue.generate(
            {"caption": "music", "auto_metas": False},
            {"seed": "42", "thinking": True}, lambda _: b"", http, sleep=lambda _: None
        )
        self.assertEqual(audio, b"wave")
        self.assertIn("song.wav", info)
        request = http.calls[0][1]["json"]
        self.assertEqual(request["prompt"], "music")
        self.assertEqual(request["seed"], 42)
        self.assertFalse(request["use_cot_metas"])
        self.assertEqual(http.calls[-1][0], local_queue.LOCAL_API + "/v1/audio")
        self.assertEqual(http.calls[-1][1]["params"], {"path": "C:\\output\\song.wav"})

    def test_cover_uploads_separate_source_and_reference_and_preserves_strengths(self):
        http = Http([{"status": 1, "result": '[{"file":"C:\\\\out.wav"}]'}])
        params = {
            "task_type": "cover", "src_audio": "source", "refer_audio": "reference",
            "remix_strength": 0.4, "cover_strength": 0.2,
        }
        local_queue.generate(params, {}, lambda audio: audio.encode(), http)
        submitted = http.calls[0][1]
        self.assertNotIn("Content-Type", submitted["headers"])
        self.assertEqual(submitted["files"]["src_audio"][1], b"source")
        self.assertEqual(submitted["files"]["reference_audio"][1], b"reference")
        self.assertEqual(submitted["data"]["audio_cover_strength"], "0.4")
        self.assertEqual(submitted["data"]["cover_noise_strength"], "0.2")
        self.assertEqual(submitted["data"]["thinking"], "false")

    def test_shared_local_queue_uses_the_configured_api_key_for_every_request(self):
        http = Http([{"status": 1, "result": '[{"file":"C:\\\\out.wav"}]'}])
        with patch.dict(os.environ, {"ACESTEP_LOCAL_API_KEY": "local-secret"}, clear=True):
            local_queue.generate({}, {}, lambda _: b"", http)
        self.assertEqual(len(http.calls), 3)
        for _, kwargs in http.calls:
            self.assertEqual(kwargs["headers"], {
                "User-Agent": "AceMusic-ComfyUI/2.0",
                "Authorization": "Bearer local-secret",
            })

    def test_rejects_unsupported_and_invalid_requests(self):
        for params in (
            {"sample_mode": True},
            {"audio_codes": "codes"},
            {"task_type": "cover"},
            {"task_type": "extract"},
        ):
            with self.subTest(params=params), self.assertRaises(ValueError):
                local_queue.build_request(params, {})
        with self.assertRaises(ValueError):
            local_queue.build_request({}, {"lm_top_p": 1.0})
        with self.assertRaises(ValueError):
            local_queue.build_request({}, {"lm_top_p": 0.0})
        with self.assertRaisesRegex(ValueError, "Auto metadata"):
            local_queue.build_request({}, {
                "thinking": False, "use_cot_caption": False, "use_cot_language": False,
            })

    def test_failure_and_untrusted_result_are_not_success(self):
        for entry in (
            {"status": 2, "result": '[{"error":"failed"}]'},
            {"status": 1, "result": '[{"file":"https://example.com/audio"}]'},
        ):
            with self.subTest(entry=entry), self.assertRaises(RuntimeError):
                local_queue.generate({}, {}, lambda _: b"", Http([entry]))

    def test_timeout_warns_that_server_can_continue(self):
        with self.assertRaisesRegex(TimeoutError, "still be running"):
            local_queue.generate({}, {}, lambda _: b"", Http([]), clock=iter([0, 3600]).__next__)


if __name__ == "__main__":
    unittest.main()
