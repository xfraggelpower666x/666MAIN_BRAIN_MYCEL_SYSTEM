"""Loopback-only, origin-checked gateway for an unmodified local ComfyUI."""

import asyncio
import re
from aiohttp import ClientError, ClientSession, ClientTimeout, TraceConfig, WSMsgType, web
from multidict import CIMultiDict


HOST = "127.0.0.1"
PORT = 8189
UPSTREAM = "http://127.0.0.1:8188"
GATEWAY_ORIGIN = f"http://{HOST}:{PORT}"
APP_ORIGINS = {"http://127.0.0.1:5174", "http://tauri.localhost"}
APP_READ_ROUTES = {"/system_stats", "/history", "/view"}
HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "transfer-encoding", "upgrade",
}

# Deliberately excludes cloud, manager, internal, and arbitrary custom-node APIs.
EXACT_GET = {
    "/", "/ws", "/system_stats", "/features", "/default_workflow", "/prompt",
    "/object_info", "/history", "/queue", "/embeddings", "/models",
    "/extensions", "/workflow_templates", "/i18n", "/node_replacements",
    "/global_subgraphs", "/users", "/userdata", "/v2/userdata", "/settings",
    "/api/jobs",
}
PREFIX_GET = (
    "/assets/", "/extensions/", "/scripts/", "/templates/", "/docs/",
    "/models/", "/object_info/", "/history/", "/view_metadata/",
    "/global_subgraphs/", "/userdata/", "/settings/", "/api/jobs/",
)
EXACT_POST = {
    "/prompt", "/queue", "/interrupt", "/free", "/history", "/upload/image",
    "/upload/mask", "/settings", "/users", "/api/jobs/cancel",
}
PREFIX_POST = ("/settings/", "/userdata/")
SESSION = web.AppKey("session", ClientSession)


def allowed_route(method, path):
    if "\\" in path or "%" in path or "//" in path or any(part in {".", ".."} for part in path.split("/")):
        return False
    # ComfyUI aliases its standard routes under /api; jobs is already /api-only.
    canonical = path[4:] if path.startswith("/api/") and not path.startswith("/api/jobs") else path
    if method in {"GET", "HEAD"}:
        return canonical == "/view" or canonical in EXACT_GET or canonical.startswith(PREFIX_GET)
    if method == "POST":
        return (canonical in EXACT_POST or canonical.startswith(PREFIX_POST)
                or bool(re.fullmatch(r"/api/jobs/[^/]+/cancel", canonical)))
    if method == "DELETE":
        return canonical.startswith("/userdata/")
    return False


def authorize(request):
    if request.headers.get("Host") != f"{HOST}:{PORT}":
        return False
    origin = request.headers.get("Origin")
    if origin and origin not in APP_ORIGINS | {GATEWAY_ORIGIN}:
        return False
    if request.method not in {"GET", "HEAD"} and origin != GATEWAY_ORIGIN:
        return False
    if request.path in {"/ws", "/api/ws"} and origin != GATEWAY_ORIGIN:
        return False
    site = request.headers.get("Sec-Fetch-Site")
    if site == "cross-site":
        return (request.method == "GET" and (
            (request.path == "/" and request.headers.get("Sec-Fetch-Dest") == "iframe")
            or (request.path in APP_READ_ROUTES and origin in APP_ORIGINS)
        ))
    return True


def response_headers(headers, request):
    result = CIMultiDict((k, v) for k, v in headers.items()
                         if k.lower() not in HOP_HEADERS | {
                             "access-control-allow-origin", "access-control-allow-credentials",
                             "cross-origin-embedder-policy", "cross-origin-resource-policy",
                         })
    result["Cross-Origin-Embedder-Policy"] = "require-corp"
    result["Cross-Origin-Resource-Policy"] = "cross-origin" if request.path == "/" else "same-origin"
    if request.path == "/":
        result.add("Content-Security-Policy",
            "frame-ancestors 'self' http://127.0.0.1:5174 http://tauri.localhost"
        )
    if request.path in APP_READ_ROUTES and request.headers.get("Origin") in APP_ORIGINS:
        result["Access-Control-Allow-Origin"] = request.headers["Origin"]
        result["Vary"] = "Origin"
    return result


async def websocket(request, session):
    async with session.ws_connect(f"{UPSTREAM}{request.rel_url}", origin=UPSTREAM) as upstream:
        downstream = web.WebSocketResponse()
        await downstream.prepare(request)

        async def relay(source, target):
            async for message in source:
                if message.type == WSMsgType.TEXT:
                    await target.send_str(message.data)
                elif message.type == WSMsgType.BINARY:
                    await target.send_bytes(message.data)
                elif message.type == WSMsgType.ERROR:
                    break

        tasks = [asyncio.create_task(relay(downstream, upstream)),
                 asyncio.create_task(relay(upstream, downstream))]
        try:
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            for task in tasks:
                task.cancel()
            await downstream.close()
        return downstream


async def handle(request):
    if not authorize(request):
        raise web.HTTPForbidden(text="Untrusted host or origin.")
    if not allowed_route(request.method, request.path):
        raise web.HTTPNotFound(text="Route not exposed by the ComfyUI gateway.")
    session = request.app[SESSION]
    try:
        async with session.get(
            f"{UPSTREAM}/system_stats", headers={"Origin": UPSTREAM},
            allow_redirects=False, timeout=ClientTimeout(total=5),
        ) as health:
            if health.headers.get("Access-Control-Allow-Origin"):
                raise web.HTTPBadGateway(text="ComfyUI CORS mode is unsafe; restart without --enable-cors-header.")
            if health.status != 200:
                raise web.HTTPBadGateway(text=f"ComfyUI health check failed: HTTP {health.status}.")
        if request.path in {"/ws", "/api/ws"}:
            return await websocket(request, session)
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in HOP_HEADERS | {
                "host", "origin", "sec-fetch-site", "content-length",
            }
        }
        headers["Origin"] = UPSTREAM
        headers["Sec-Fetch-Site"] = "same-origin"
        async with session.request(
            request.method, f"{UPSTREAM}{request.rel_url}", headers=headers,
            data=request.content.iter_chunked(65536) if request.can_read_body else None,
            allow_redirects=False,
        ) as upstream:
            if upstream.headers.get("Access-Control-Allow-Origin"):
                raise web.HTTPBadGateway(text="ComfyUI CORS mode is unsafe; restart without --enable-cors-header.")
            if 300 <= upstream.status < 400 and upstream.status != 304:
                raise web.HTTPBadGateway(text="Unexpected ComfyUI redirect.")
            response = web.StreamResponse(
                status=upstream.status, headers=response_headers(upstream.headers, request),
            )
            await response.prepare(request)
            async for chunk in upstream.content.iter_chunked(65536):
                await response.write(chunk)
            await response.write_eof()
            return response
    except (ClientError, asyncio.TimeoutError, UnsafeRedirect) as exc:
        raise web.HTTPBadGateway(text=f"Cannot connect to local ComfyUI: {exc}") from exc


class UnsafeRedirect(Exception):
    pass


async def reject_redirect(_session, _context, _params):
    raise UnsafeRedirect("Upstream redirects are not permitted.")


async def client_context(app):
    # Trace the WebSocket handshake as well as regular HTTP: neither may redirect.
    trace = TraceConfig()
    trace.on_request_redirect.append(reject_redirect)
    async with ClientSession(timeout=ClientTimeout(total=None, connect=5),
                             auto_decompress=False, trace_configs=[trace]) as session:
        app[SESSION] = session
        yield


def create_app():
    app = web.Application(client_max_size=1024**3)
    app.cleanup_ctx.append(client_context)
    app.router.add_route("*", "/{tail:.*}", handle)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host=HOST, port=PORT, print=None)
