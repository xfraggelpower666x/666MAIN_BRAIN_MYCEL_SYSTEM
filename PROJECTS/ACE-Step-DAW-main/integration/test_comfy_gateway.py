import unittest

from aiohttp import ClientSession, WSMsgType, web
from aiohttp.test_utils import TestServer

import comfy_gateway as gateway


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.saved = gateway.PORT, gateway.GATEWAY_ORIGIN, gateway.UPSTREAM
        self.requests = []
        self.cors = False
        self.redirect = False

        async def upstream(request):
            self.requests.append((request.method, request.path, request.headers.get("Origin")))
            if request.path == "/system_stats":
                headers = {"Access-Control-Allow-Origin": "*"} if self.cors else {}
                return web.json_response({"system": {}, "devices": []}, headers=headers)
            if request.path == "/ws":
                ws = web.WebSocketResponse()
                await ws.prepare(request)
                await ws.send_str("ready")
                async for message in ws:
                    if message.type == WSMsgType.TEXT:
                        await ws.send_str(message.data)
                return ws
            if self.redirect:
                raise web.HTTPFound("https://example.invalid/")
            return web.Response(body=await request.read() or b"ok")

        upstream_app = web.Application()
        upstream_app.router.add_route("*", "/{tail:.*}", upstream)
        self.upstream = TestServer(upstream_app, host="127.0.0.1")
        await self.upstream.start_server()
        gateway.UPSTREAM = str(self.upstream.make_url("")).rstrip("/")
        self.server = TestServer(gateway.create_app(), host="127.0.0.1")
        await self.server.start_server()
        gateway.PORT = self.server.port
        gateway.GATEWAY_ORIGIN = f"http://127.0.0.1:{gateway.PORT}"
        self.client = ClientSession()

    async def asyncTearDown(self):
        await self.client.close()
        await self.server.close()
        await self.upstream.close()
        gateway.PORT, gateway.GATEWAY_ORIGIN, gateway.UPSTREAM = self.saved

    async def request(self, method, path, **kwargs):
        return await self.client.request(method, self.server.make_url(path), **kwargs)

    async def test_untrusted_origins_and_hosts_cannot_mutate(self):
        for headers in (
            {"Origin": "https://evil.example"},
            {"Origin": "http://127.0.0.1:5174"},
            {"Origin": gateway.GATEWAY_ORIGIN, "Host": "evil.example"},
            {},
        ):
            with self.subTest(headers=headers):
                response = await self.request("POST", "/prompt", headers=headers, json={})
                self.assertEqual(response.status, 403)
        self.assertEqual(self.requests, [])

    async def test_allowed_mutation_uses_upstream_origin_and_blocks_unknown_routes(self):
        response = await self.request(
            "POST", "/prompt", headers={"Origin": gateway.GATEWAY_ORIGIN}, data=b"payload"
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(await response.read(), b"payload")
        self.assertIn(("POST", "/prompt", gateway.UPSTREAM), self.requests)
        response = await self.request(
            "POST", "/internal/sensitive", headers={"Origin": gateway.GATEWAY_ORIGIN}
        )
        self.assertEqual(response.status, 404)

    async def test_cors_mode_is_rejected_before_forwarding_mutation(self):
        self.cors = True
        response = await self.request("POST", "/prompt", headers={"Origin": gateway.GATEWAY_ORIGIN})
        self.assertEqual(response.status, 502)
        self.assertNotIn("POST", [item[0] for item in self.requests])

    async def test_upstream_redirects_are_not_followed(self):
        self.redirect = True
        response = await self.request("GET", "/history")
        self.assertEqual(response.status, 502)

    async def test_parent_health_and_frame_have_narrow_cross_origin_permissions(self):
        response = await self.request("GET", "/system_stats", headers={
            "Origin": "http://tauri.localhost", "Sec-Fetch-Site": "cross-site",
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://tauri.localhost")
        self.assertEqual(response.headers["Cross-Origin-Resource-Policy"], "same-origin")
        response = await self.request("GET", "/", headers={
            "Sec-Fetch-Site": "cross-site", "Sec-Fetch-Dest": "iframe",
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Cross-Origin-Resource-Policy"], "cross-origin")
        self.assertIn("frame-ancestors", response.headers["Content-Security-Policy"])
        response = await self.request("GET", "/view", headers={"Sec-Fetch-Site": "cross-site"})
        self.assertEqual(response.status, 403)

    async def test_websocket_relay_and_origin_validation(self):
        with self.assertRaises(Exception):
            async with self.client.ws_connect(self.server.make_url("/ws"), origin="https://evil.example"):
                pass
        async with self.client.ws_connect(self.server.make_url("/ws"), origin=gateway.GATEWAY_ORIGIN) as ws:
            self.assertEqual((await ws.receive()).data, "ready")
            await ws.send_str("ping")
            self.assertEqual((await ws.receive()).data, "ping")
        self.assertIn(("GET", "/ws", gateway.UPSTREAM), self.requests)

    def test_route_allowlist_rejects_traversal_and_arbitrary_api(self):
        for path in ("/api/cloud", "/userdata/../settings", "/userdata/%2e%2e", "/userdata//x"):
            self.assertFalse(gateway.allowed_route("GET", path), path)


if __name__ == "__main__":
    unittest.main()
