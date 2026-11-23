"""666TDI R1.1 local visual daemon: a read-only UI over the R1.0 engine.

Start: python -m engine.daemon_cli --port 8766
Only localhost; no Suno API calls, no repository writes, no automatic track files.
"""
from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from . import creative_causal, semantic_intelligence, track_preanalysis, device_output, creator_learning
from . import portable

SYSTEM_ID = "666TDI-001"
DAEMON_SCHEMA = "666TDI_DAEMON_R11_LOCAL_V1"
DEVICES = {"IPHONE_SUNO_APP", "PC_SUNO_BROWSER"}
ALLOWED_FIELDS = (
    "title", "genre", "story", "motor", "mid", "high", "voice", "lyrics",
    "structure", "psychoacoustics", "energy", "atmosphere", "ending", "avoid"
)
STATIC = Path(__file__).resolve().parent / "daemon_static" / "index.html"
MAX_REQUEST_BYTES = 65536


def preanalysis(payload: dict) -> dict:
    """No persistent side effects. The creator must select the Suno device first."""
    if not isinstance(payload, dict):
        raise ValueError("INVALID_REQUEST")
    device = payload.get("device")
    if device not in DEVICES:
        raise ValueError("DEVICE_PREFLIGHT_REQUIRED")
    original = payload.get("intent")
    if not isinstance(original, dict):
        raise ValueError("INTENT_OBJECT_REQUIRED")
    intent = {}
    for key in ALLOWED_FIELDS:
        value = original.get(key, "")
        if not isinstance(value, str) or len(value) > 12000:
            raise ValueError("INVALID_FIELD:" + key)
        intent[key] = value
    if not any(intent.get(key, "").strip() for key in ("story","motor","mid","high","voice","lyrics","energy","structure")):
        raise ValueError("MUSICAL_INTENT_REQUIRED")
    bpm = original.get("bpm", "")
    if bpm not in ("", None):
        try:
            bpm = int(bpm)
        except (ValueError, TypeError):
            raise ValueError("INVALID_BPM") from None
        if not 1 <= bpm <= 350:
            raise ValueError("INVALID_BPM")
    else:
        bpm = None
    intent["bpm"] = bpm
    bars = payload.get("total_bars", None)
    if bars in ("", None):
        bars = None
    else:
        try:
            if isinstance(bars, bool) or str(bars).strip() != str(int(bars)):
                raise ValueError("INVALID_BAR_TARGET")
            bars = int(bars)
        except (ValueError, TypeError):
            raise ValueError("INVALID_BAR_TARGET") from None
        if not 32 <= bars <= 2048:
            raise ValueError("INVALID_BAR_TARGET")
    # R1.0 and R0.9 remain the only musical analysis engines.
    semantic = semantic_intelligence.assess(intent)
    causal = creative_causal.assess(intent)
    preanalysis = track_preanalysis.assess(intent, semantic, causal, total_bars=bars)
    renderer = device_output.translate(intent, device, payload.get("route_context"))
    device_labels = {
        "IPHONE_SUNO_APP": "iPhone · Suno App",
        "PC_SUNO_BROWSER": "PC · Suno Browser",
    }
    return {
        "schema": "666TDI_DAEMON_R13_LOCAL_V1",
        "system_id": SYSTEM_ID,
        "device": device,
        "device_label": device_labels[device],
        "device_profile_status": "CREATOR_SELECTED_FIELDS_NOT_LIVE_PROVIDER_VERIFIED",
        "stage": "CREATOR_DECISION_REVIEW",
        "intent": intent,
        "semantic": semantic,
        "causal": causal,
        "preanalysis": preanalysis,
        "device_output": renderer,
        "menu": [
            {"id":"device", "label":"Gerät & Workflow", "status":"COMPLETE"},
            {"id":"intent", "label":"Track-Idee", "status":"COMPLETE"},
            {"id":"analysis", "label":"Musikalische Voranalyse", "status":"COMPLETE"},
            {"id":"decisions", "label":"Entscheidungshilfen", "status":"CREATOR_REVIEW"},
            {"id":"output", "label":"Suno-Übergabe", "status":"CREATOR_REVIEW_NO_RENDER"},
        ],
        "evidence_class": "TRACK_INTENT_RULE_DERIVED_HYPOTHESIS",
        "audio_verified": False,
        "renderer_executed": False,
        "suno_generation": False,
        "requires_creator_decision": bool(causal.get("decisions") or causal.get("collisions")),
        "read_only": True,
        "no_global_learning": True,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "666TDI-Daemon/1.4"

    def log_message(self, format, *args):
        # Avoid logging submitted lyrics, creative intent or other body content.
        return

    def _send(self, status, content, mime="application/json; charset=utf-8"):
        body = content.encode("utf-8") if isinstance(content, str) else content
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _safe_host(self):
        # Localhost bind alone does not prevent DNS-rebinding requests.
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1:
            return False
        raw = hosts[0].strip()
        if not raw or any(ch in raw for ch in "/?#@\\"):
            return False
        try:
            parsed = urlsplit("//" + raw)
            return (parsed.hostname in ("localhost", "127.0.0.1")
                    and parsed.port == self.server.server_port
                    and not parsed.username and not parsed.password)
        except ValueError:
            return False

    def _safe_origin(self):
        origin = self.headers.get("Origin", "")
        if not origin:
            # Non-browser clients may omit Origin but still must pass the Host gate.
            return True
        try:
            parsed = urlsplit(origin)
            return (parsed.scheme == "http"
                    and parsed.hostname in ("localhost", "127.0.0.1")
                    and parsed.port == self.server.server_port
                    and not parsed.username and not parsed.password
                    and not parsed.path and not parsed.query and not parsed.fragment)
        except ValueError:
            return False

    def do_GET(self):
        if not self._safe_host():
            self._json(403, {"error": "HOST_NOT_ALLOWED"})
            return
        if self.path in ("/", "/index.html"):
            self._send(200, STATIC.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/status":
            self._json(200, {
                "schema": DAEMON_SCHEMA,
                "system_id": SYSTEM_ID,
                "status": "LOCAL_VISUAL_DAEMON_READY",
                "engine": "R1.0_CREATIVE_CAUSAL",
                "device_required": True,
                "suno_connected": False,
                "read_only": False,
                "preanalysis_read_only": True,
                "feedback_requires_explicit_creator_confirmation": True,
                "feedback_writes_local": True,
                "global_learning": False
            })
        else:
            self._json(404, {"error": "NOT_FOUND"})

    def do_POST(self):
        if not self._safe_host():
            self._json(403, {"error": "HOST_NOT_ALLOWED"})
            return
        if self.path not in ("/api/preanalysis", "/api/feedback", "/api/learning/read"):
            self._json(404, {"error": "NOT_FOUND"})
            return
        if not self._safe_origin():
            self._json(403, {"error": "ORIGIN_NOT_ALLOWED"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self._json(415, {"error": "JSON_REQUIRED"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "INVALID_LENGTH"})
            return
        if size <= 0 or size > MAX_REQUEST_BYTES:
            self._json(413, {"error": "REQUEST_SIZE_INVALID"})
            return
        try:
            request = json.loads(self.rfile.read(size))
            if self.path == "/api/preanalysis":
                output = preanalysis(request)
            elif self.path == "/api/feedback":
                output = creator_learning.record(portable.DATA, request)
            else:
                if not isinstance(request, dict):
                    raise ValueError("INVALID_LEARNING_REQUEST")
                output = creator_learning.assess(portable.DATA, request.get("track_id"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return
        self._json(200, output)


def main():
    parser = argparse.ArgumentParser(description="666TDI local visual daemon")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    host = "127.0.0.1"
    with ThreadingHTTPServer((host, args.port), Handler) as server:
        print("666TDI DAEMON R1.4 · http://%s:%s" % (host, args.port))
        print("LOCAL ONLY · DEVICE PREFLIGHT REQUIRED · NO SUNO EXECUTION")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
