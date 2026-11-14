import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from suno_mcp_server import handle_list_tools
from sunoapi_client import SunoClient


class SunoMCPTests(unittest.IsolatedAsyncioTestCase):
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
