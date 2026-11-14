import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.types import CallToolResult

from suno_mcp_server import handle_call_tool, handle_list_tools
from sunoapi_client import SunoClient


class SunoMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_task_status_includes_snake_case_generation_urls(self):
        client = type("Client", (), {})()
        client.get_task_status = AsyncMock(return_value={
            "data": {
                "taskId": "task-1",
                "status": "SUCCESS",
                "response": {
                    "sunoData": [{
                        "audio_url": "https://example.test/audio.mp3",
                        "stream_audio_url": "https://example.test/stream",
                        "image_url": "https://example.test/cover.jpg",
                    }]
                },
            }
        })

        with patch("suno_mcp_server.suno_client", client):
            result = await handle_call_tool("get_task_status", {"task_id": "task-1"})

        text = result[0].text
        self.assertIn("Audio URL: https://example.test/audio.mp3", text)
        self.assertIn("Stream URL: https://example.test/stream", text)
        self.assertIn("Image URL: https://example.test/cover.jpg", text)

    async def test_task_status_reports_terminal_generation_failure_details(self):
        client = type("Client", (), {})()
        client.get_task_status = AsyncMock(return_value={
            "data": {
                "taskId": "task-1",
                "status": "GENERATE_AUDIO_FAILED",
                "errorCode": "AUDIO_ERROR",
                "errorMessage": "Generation failed",
            }
        })

        with patch("suno_mcp_server.suno_client", client):
            result = await handle_call_tool("get_task_status", {"task_id": "task-1"})

        text = result[0].text
        self.assertIn("Generation failed.", text)
        self.assertIn("Error Code: AUDIO_ERROR", text)
        self.assertIn("Error Message: Generation failed", text)
        self.assertNotIn("Generation in progress", text)

    async def test_provider_exceptions_are_returned_as_mcp_errors(self):
        client = type("Client", (), {})()
        client.get_task_status = AsyncMock(side_effect=RuntimeError("provider unavailable"))

        with patch("suno_mcp_server.suno_client", client):
            result = await handle_call_tool("get_task_status", {"task_id": "task-1"})

        self.assertIsInstance(result, CallToolResult)
        self.assertTrue(result.isError)
        self.assertIn("provider unavailable", result.content[0].text)

    async def test_server_exposes_all_suno_mcp_tools(self):
        tools = await handle_list_tools()

        self.assertEqual(
            {tool.name for tool in tools},
            {
                "generate_music",
                "get_task_status",
                "get_music_info",
                "get_credits",
                "convert_to_wav",
                "get_wav_conversion_status",
            },
        )
        music_info = next(tool for tool in tools if tool.name == "get_music_info")
        self.assertEqual(music_info.inputSchema["required"], ["task_id"])

    async def test_get_music_info_uses_generation_task_id(self):
        client = type("Client", (), {})()
        client.get_music_info = AsyncMock(return_value={"data": []})

        with patch("suno_mcp_server.suno_client", client):
            result = await handle_call_tool(
                "get_music_info",
                {"task_id": "generation-task"},
            )

        client.get_music_info.assert_awaited_once_with("generation-task")
        self.assertIn("Music Track Information", result[0].text)

    async def test_waited_generation_reports_completed_tracks(self):
        client = type("Client", (), {})()
        client.generate_music = AsyncMock(return_value={
            "data": {
                "taskId": "generation-task",
                "status": "SUCCESS",
                "response": {
                    "sunoData": [{
                        "id": "track-id",
                        "title": "Completed song",
                        "audio_url": "https://example.test/completed.mp3",
                    }]
                },
            }
        })

        with patch("suno_mcp_server.suno_client", client):
            result = await handle_call_tool(
                "generate_music",
                {"prompt": "A song", "wait_audio": True},
            )

        text = result[0].text
        self.assertIn("Music generation completed", text)
        self.assertIn("Generated 1 track(s)", text)
        self.assertIn("Task ID: generation-task", text)
        self.assertIn("Audio URL: https://example.test/completed.mp3", text)
        self.assertNotIn("processing asynchronously", text)

    def test_api_key_client_uses_only_the_configured_api_key_provider(self):
        with patch.dict(
            os.environ,
            {
                "SUNO_API_KEY": "test-api-key",
                "SUNO_API_BASE_URL": "https://api.sunoapi.org",
                "SUNO_SESSION_COOKIE": "__client=manager-cookie",
            },
            clear=True,
        ), patch("sunoapi_client.httpx.AsyncClient") as async_client:
            SunoClient()

        kwargs = async_client.call_args.kwargs
        self.assertEqual(kwargs["base_url"], "https://api.sunoapi.org")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-api-key")

    def test_manager_cookie_does_not_replace_missing_api_key(self):
        with patch.dict(
            os.environ,
            {"SUNO_SESSION_COOKIE": "__client=manager-cookie"},
            clear=True,
        ):
            with self.assertRaisesRegex(ValueError, "SUNO_API_KEY"):
                SunoClient()


if __name__ == "__main__":
    unittest.main()
