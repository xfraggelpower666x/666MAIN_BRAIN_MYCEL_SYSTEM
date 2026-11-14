import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sunoapi_client import SunoAPIError, SunoClient


def json_response(body):
    return SimpleNamespace(
        raise_for_status=Mock(),
        json=Mock(return_value=body),
    )


class SunoAPIClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.suno = SunoClient.__new__(SunoClient)
        self.suno.client = SimpleNamespace(
            post=AsyncMock(),
            get=AsyncMock(),
        )

    async def test_generate_music_waits_for_terminal_success(self):
        self.suno.client.post.return_value = json_response(
            {"code": 200, "data": {"taskId": "generation-task"}}
        )
        self.suno.client.get.side_effect = [
            json_response({"code": 200, "data": {"status": "PENDING"}}),
            json_response(
                {
                    "code": 200,
                    "data": {
                        "status": "SUCCESS",
                        "response": {"sunoData": [{"id": "track-id"}]},
                    },
                }
            ),
        ]

        with patch("sunoapi_client.asyncio.sleep", new_callable=AsyncMock) as sleep:
            result = await self.suno.generate_music(prompt="A song")

        self.assertEqual(result["data"]["status"], "SUCCESS")
        self.assertNotIn("wait_audio", self.suno.client.post.call_args.kwargs["json"])
        self.assertEqual(
            self.suno.client.get.call_args_list[0].kwargs["params"],
            {"taskId": "generation-task"},
        )
        sleep.assert_awaited_once()

    async def test_generate_music_can_return_asynchronous_submission(self):
        submission = {"code": 200, "data": {"taskId": "generation-task"}}
        self.suno.client.post.return_value = json_response(submission)

        result = await self.suno.generate_music(prompt="A song", wait_audio=False)

        self.assertEqual(result, submission)
        self.suno.client.get.assert_not_awaited()

    async def test_get_music_info_looks_up_generation_task_id(self):
        details = {
            "code": 200,
            "data": {
                "status": "SUCCESS",
                "response": {"sunoData": [{"id": "track-id"}]},
            },
        }
        self.suno.client.get.return_value = json_response(details)

        result = await self.suno.get_music_info("generation-task")

        self.assertEqual(result["data"], [{"id": "track-id"}])
        self.suno.client.get.assert_awaited_once_with(
            "/api/v1/generate/record-info",
            params={"taskId": "generation-task"},
        )

    async def test_get_music_info_requires_a_generation_task_id(self):
        for invalid_task_id in ("", ["track-id"]):
            with self.subTest(task_id=invalid_task_id):
                with self.assertRaisesRegex(ValueError, "task_id is required"):
                    await self.suno.get_music_info(invalid_task_id)

    async def test_generate_music_raises_on_terminal_failure(self):
        self.suno.client.post.return_value = json_response(
            {"code": 200, "data": {"taskId": "generation-task"}}
        )
        self.suno.client.get.return_value = json_response(
            {
                "code": 200,
                "data": {
                    "status": "GENERATE_AUDIO_FAILED",
                    "errorMessage": "generation failed",
                },
            }
        )

        with self.assertRaisesRegex(SunoAPIError, "generation failed"):
            await self.suno.generate_music(prompt="A song")


if __name__ == "__main__":
    unittest.main()
