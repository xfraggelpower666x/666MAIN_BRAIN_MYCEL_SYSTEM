"""Claude on your own plan, for 3DX Profile Studio on this PC.

A small local server that speaks the OpenAI chat API and answers with the Claude CLI, signed in with your own
Claude subscription. In the Studio: AI settings > "Local or custom", server address http://127.0.0.1:8788/v1,
then Load models (opus, sonnet, haiku).

It is for your own use on your own PC. A Claude plan is personal, so it listens on 127.0.0.1 only and answers
only the Studio's pages. It never falls back to an API key: ANTHROPIC_API_KEY is removed before the CLI runs.

    python tools/plan_bridge.py                 port 8788, effort low
    python tools/plan_bridge.py --port 9000 --effort medium

The CLI is CLAUDE_CLI, else `claude` on the PATH, else the newest VS Code extension's own. Sign it in once with
`claude` and /login. Your Claude memory, CLAUDE.md files, tools and MCP servers are all switched off for these
calls, so nothing personal ends up in a profile.
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ORIGINS = {"https://deaeath.github.io", "null"}   # the published Studio, and a downloaded copy opened from disk
MODELS = ["opus", "sonnet", "haiku"]              # the first is the Studio's default pick
TIMEOUT = 300                                     # seconds before a stuck answer is stopped
AT_ONCE = threading.BoundedSemaphore(2)           # answers running at the same time
WORKDIR = os.path.join(tempfile.gettempdir(), "plan-bridge")   # an empty folder: no project files for the CLI to read
EFFORT = "low"


def claude_cli():
    """The Claude CLI: CLAUDE_CLI, else `claude` on the PATH, else the VS Code extension's own (the newest)."""
    if os.environ.get("CLAUDE_CLI"):
        return os.environ["CLAUDE_CLI"]
    found = shutil.which("claude")
    if found:
        return found
    exts = sorted(glob.glob(os.path.join(os.path.expanduser("~"), ".vscode", "extensions", "anthropic.claude-code-*",
                                         "resources", "native-binary", "claude*")), key=os.path.getmtime)
    if not exts:
        sys.exit("No Claude CLI found: install Claude Code, or set CLAUDE_CLI to its path.")
    return exts[-1]


def cli_env():
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):   # the plan only: never per-token billing
        env.pop(k, None)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    return env


def allowed(origin):
    return (not origin or origin in ORIGINS or origin.startswith("http://localhost:")
            or origin.startswith("http://127.0.0.1:"))


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return ""


def split_messages(messages):
    """OpenAI messages -> (system prompt, the user's prompt). A longer chat becomes a labelled transcript."""
    system = "\n\n".join(text_of(m.get("content")) for m in messages if m.get("role") in ("system", "developer"))
    rest = [m for m in messages if m.get("role") in ("user", "assistant")]
    if len(rest) == 1:
        return system, text_of(rest[0].get("content"))
    lines = [("User: " if m["role"] == "user" else "Assistant: ") + text_of(m.get("content")) for m in rest]
    return system, "\n\n".join(lines) + "\n\nReply as the assistant to the last user message."


def plain_error(text):
    t = str(text or "")
    if any(w in t.lower() for w in ("not logged in", "/login", "invalid api key", "oauth")):
        return 401, "Claude isn't signed in on this PC. Run `claude` in a terminal and use /login."
    if "limit" in t.lower():
        return 429, "Your Claude plan's usage limit is reached. Try again when it resets."
    return 502, "Claude couldn't answer: " + (t.strip()[:300] or "no reason given")


class Bridge(BaseHTTPRequestHandler):
    server_version = "PlanBridge/1"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):   # one short line per request, never the text itself
        sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def cors(self):
        origin = self.headers.get("Origin", "")
        h = {"Vary": "Origin"}
        if origin and allowed(origin):
            h["Access-Control-Allow-Origin"] = origin
        return h

    def reply(self, status, body, extra=None):
        data = json.dumps(body).encode("utf-8")
        self.close_connection = True   # one request per connection: an unread body is never parsed as a request
        self.send_response(status)
        for k, v in {**self.cors(), **(extra or {}), "Content-Type": "application/json", "Content-Length": str(len(data)),
                     "Cache-Control": "no-store", "Connection": "close"}.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def error(self, status, message, kind="api_error"):
        self.reply(status, {"error": {"message": message, "type": kind}})

    def do_OPTIONS(self):
        if not allowed(self.headers.get("Origin", "")):
            self.send_response(403)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(204)
        for k, v in {**self.cors(), "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                     "Access-Control-Allow-Headers": "Content-Type, Authorization",
                     "Access-Control-Allow-Private-Network": "true",   # Chrome: a public page asking 127.0.0.1
                     "Access-Control-Max-Age": "86400", "Content-Length": "0"}.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if not allowed(self.headers.get("Origin", "")):
            return self.error(403, "This bridge only answers 3DX Profile Studio.")
        if self.path.rstrip("/") in ("/v1/models", "/models"):
            return self.reply(200, {"object": "list", "data": [{"id": m, "object": "model", "owned_by": "your Claude plan"}
                                                               for m in MODELS]})
        if self.path in ("/", "/v1"):
            return self.reply(200, {"ok": True, "service": "plan-bridge", "models": MODELS})
        self.error(404, "Not found.")

    def do_POST(self):
        if not allowed(self.headers.get("Origin", "")):
            return self.error(403, "This bridge only answers 3DX Profile Studio.")
        if self.path.rstrip("/") not in ("/v1/chat/completions", "/chat/completions"):
            return self.error(404, "Not found.")
        if "application/json" not in self.headers.get("Content-Type", ""):
            return self.error(415, "Send JSON.")
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.error(400, "Bad JSON.")
        system, prompt = split_messages(body.get("messages") or [])
        if not prompt.strip():
            return self.error(400, "Nothing to answer.")
        model = str(body.get("model") or MODELS[0])
        if model not in MODELS and not model.startswith("claude-"):
            model = MODELS[0]
        if not AT_ONCE.acquire(timeout=60):
            return self.error(429, "The bridge is busy with other answers. Try again in a moment.")
        try:
            self.answer(system, prompt, model, bool(body.get("stream")))
        finally:
            AT_ONCE.release()

    def answer(self, system, prompt, model, stream):
        os.makedirs(WORKDIR, exist_ok=True)
        settings = os.path.join(WORKDIR, "settings.json")   # (a file, not a JSON argument: safe through any shim)
        if not os.path.isfile(settings):
            with open(settings, "w", encoding="utf-8") as f:
                json.dump({"autoMemoryEnabled": False}, f)
        sysfile = os.path.join(WORKDIR, f"system-{uuid.uuid4().hex}.txt")
        with open(sysfile, "w", encoding="utf-8") as f:
            f.write(system or "You are a helpful writing assistant.")
        cmd = [claude_cli(), "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
               "--no-session-persistence", "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
               "--setting-sources", "", "--settings", settings,
               "--system-prompt-file", sysfile, "--model", model]
        if EFFORT:
            cmd += ["--effort", EFFORT]
        proc = subprocess.Popen(cmd, cwd=WORKDIR, env=cli_env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        err = []
        threading.Thread(target=lambda: err.extend(proc.stderr), daemon=True).start()   # (a full pipe stalls the CLI)
        killer = threading.Timer(TIMEOUT, proc.kill)
        killer.start()
        cid, created = "chatcmpl-" + uuid.uuid4().hex[:24], int(time.time())
        chunk = lambda delta, finish=None: {"id": cid, "object": "chat.completion.chunk", "created": created, "model": model,
                                            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
        text, stop, failure, started = "", "stop", None, False
        try:
            proc.stdin.write(prompt)
            proc.stdin.close()
            for line in proc.stdout:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("type") == "stream_event":
                    e = ev.get("event") or {}
                    d = e.get("delta") or {}
                    if e.get("type") == "content_block_delta" and d.get("type") == "text_delta" and d.get("text"):
                        text += d["text"]
                        if stream:
                            if not started:
                                self.start_stream()
                                started = True
                            self.event(chunk({"content": d["text"]}))
                    if e.get("type") == "message_delta" and d.get("stop_reason") == "max_tokens":
                        stop = "length"
                elif ev.get("type") == "result" and (ev.get("is_error") or ev.get("subtype") != "success"):
                    failure = ev.get("result") or ev.get("subtype") or "error"
            proc.wait(timeout=30)
            if not text and failure is None and proc.returncode:
                failure = "".join(err)[-400:] or f"the CLI stopped (exit {proc.returncode})"
            if not stream:
                if failure and not text:
                    status, msg = plain_error(failure)
                    return self.error(status, msg)
                return self.reply(200, {"id": cid, "object": "chat.completion", "created": created, "model": model,
                                        "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                                                     "finish_reason": stop}]})
            if failure and not text:
                if not started:
                    status, msg = plain_error(failure)
                    return self.error(status, msg)
                self.event({"error": {"message": plain_error(failure)[1]}})
            if not started:
                self.start_stream()
            self.event(chunk({}, stop))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            proc.kill()   # the Studio pressed Stop or closed
        finally:
            killer.cancel()
            if proc.poll() is None:
                proc.kill()
            try:
                os.remove(sysfile)
            except OSError:
                pass
            self.close_connection = True

    def start_stream(self):
        self.send_response(200)
        for k, v in {**self.cors(), "Content-Type": "text/event-stream", "Cache-Control": "no-store",
                     "Connection": "close"}.items():
            self.send_header(k, v)
        self.end_headers()

    def event(self, obj):
        self.wfile.write(("data: " + json.dumps(obj) + "\n\n").encode("utf-8"))
        self.wfile.flush()


def main():
    global EFFORT
    ap = argparse.ArgumentParser(description="Claude on your own plan, for 3DX Profile Studio on this PC.")
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--effort", default=EFFORT, choices=["low", "medium", "high", "xhigh", "max", ""],
                    help="how hard Claude thinks (low is fast and plenty for profiles)")
    args = ap.parse_args()
    EFFORT = args.effort
    print(f"Claude CLI: {claude_cli()}")
    print(f"Plan bridge on http://127.0.0.1:{args.port}/v1  (Studio: AI settings > Local or custom). Ctrl+C stops it.")
    ThreadingHTTPServer(("127.0.0.1", args.port), Bridge).serve_forever()


if __name__ == "__main__":
    main()
