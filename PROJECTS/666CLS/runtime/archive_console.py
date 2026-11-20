"""Menü für registrierte Frameworks und das gemeinsame 666CLS-Archiv."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sqlite3
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from cls_livecircle import DOMAINS, ROOT, SYSTEM, json_text, read, rehydrate, require
from dashboard import render_dashboard
from framework_intake import analyze
from shared_archive import CLIENT_ID, authorize, inbox_counts, live_records, pending, prepare, submit

LIMIT = 1024 * 1024
ACTIONS = {"start": "Starten", "resume": "Fortsetzen"}

# Read-only references are not archive clients and never grant execution rights.
# UMIP remains child of 666PFS; CTGLE remains its add-on.
FRAMEWORK_REFERENCES = (
    {"id": "pfs-umip-4001", "name": "666UMIP (666PFS-Child)",
     "authority": "666PFS-CORE-001 / 666PFS_CSM / UMIP-4001",
     "revision": "1.11.1 · READY_FOR_MANUAL_SELECTION · CTGLE: Add-on",
     "actions": [], "read": [], "submit": []},
)


def validate_action(action):
    trigger = action["trigger"]
    require(isinstance(trigger, str) and trigger.strip() and len(trigger.splitlines()) == 1,
            "Nativer Trigger fehlt oder ist ungültig")
    require(action["mode"] in ("chat", "local"), "Unbekannter Framework-Aktionsmodus")
    if action["mode"] == "local":
        argv = action["argv"]
        require(isinstance(argv, list) and argv and all(isinstance(arg, str) for arg in argv),
                "Lokale Aktion benötigt feste Argumente")
        require(Path(argv[0]).is_absolute() and Path(action["cwd"]).is_absolute(),
                "Lokale Aktion benötigt absolute Adapter- und Arbeitspfade")


class Console:
    def __init__(self, root, private, operator):
        self.root, self.private, self.operator = root, private, operator
        self.db = private / "inbox.sqlite3"

    def registry(self):
        config = read(self.private / "frameworks.json")
        policy = read(self.private / "clients.json")
        require(policy["system_id"] == SYSTEM, "Falsche System-ID in der Zugriffskonfiguration")
        clients = policy["clients"]
        frameworks = {}
        for key, item in config["frameworks"].items():
            require(CLIENT_ID.fullmatch(key) and key in clients, "Framework-Kennung ungültig oder ohne Archivprofil")
            require(all(isinstance(item[k], str) and item[k].strip() for k in ("name", "authority", "revision")),
                    "Framework braucht Name, Authority und verifizierte Revision")
            require(isinstance(item["actions"], dict) and item["actions"].keys() <= ACTIONS.keys(),
                    "Unbekannte Framework-Aktion")
            for action in item["actions"].values():
                validate_action(action)
            profile = clients[key]
            for permission in ("read", "submit"):
                domains = profile.get(permission, [])
                require(isinstance(domains, list) and all(domain in DOMAINS for domain in domains),
                        "Archivprofil enthält einen ungültigen Bereich")
            frameworks[key] = (item, profile)
        return frameworks

    def model(self):
        state = rehydrate(self.root)
        frameworks = self.registry()
        result = [{"id": key, "name": item["name"], "authority": item["authority"],
                   "revision": item["revision"],
                   "actions": [{"id": name, "label": ACTIONS[name], "mode": config["mode"]}
                               for name, config in item["actions"].items()],
                   "read": profile.get("read", []), "submit": profile.get("submit", [])}
                  for key, (item, profile) in frameworks.items()]
        existing = {item["id"] for item in result}
        result.extend(dict(item) for item in FRAMEWORK_REFERENCES if item["id"] not in existing)
        return {"archive_version": state["version"], "counts": state["domains"],
                "frameworks": result}

    def overview(self, output):
        state = rehydrate(self.root)
        render_dashboard(self.root, state, output, inbox=inbox_counts(self.db, self.root, state))

    def handle(self, request):
        command = request["command"]
        if command == "analyze":
            registry = {key: item for key, (item, _) in self.registry().items()}
            return analyze(request["dossier"], registry)
        if command == "pending":
            return {"entries": pending(self.db, self.root)}
        if command == "prepare":
            version = request["version"]
            candidate = prepare(self.db, self.root, version, request["receipts"])
            with TemporaryDirectory(prefix=".candidate-", dir=self.private) as folder:
                stage = Path(folder) / "candidate.json"
                stage.write_text(json_text(candidate), encoding="utf-8")
                path = self.private / f"666cls-candidate-{version}.json"
                os.link(stage, path)
            return {"status": "CANDIDATE", "file": path.name, "base_version": candidate["base_version"]}
        key = request["framework"]
        frameworks = self.registry()
        require(key in frameworks, "Framework ist nicht registriert")
        framework, profile = frameworks[key]
        if command == "framework":
            name = request["action"]
            require(name in framework["actions"], "Aktion ist für dieses Framework nicht registriert")
            action = framework["actions"][name]
            if action["mode"] == "chat":
                return {"status": "HANDOFF", "trigger": action["trigger"], "authority": framework["authority"],
                        "revision": framework["revision"]}
            argv = action["argv"]
            executable, cwd = Path(argv[0]), Path(action["cwd"])
            require(executable.is_file() and cwd.is_dir(),
                    "Lokaler Framework-Adapter ist nicht verfügbar")
            env = {k: v for k, v in os.environ.items() if k != "CLS_ARCHIVE_TOKEN"}
            result = subprocess.run(argv, shell=False, cwd=cwd, env=env, capture_output=True,
                                    text=True, errors="replace", timeout=30)
            return {"status": "AUSGEFÜHRT" if result.returncode == 0 else "BLOCKIERT",
                    "exit_code": result.returncode, "output": result.stdout[-8000:],
                    "error": result.stderr[-8000:]}
        domain = request["domain"]
        require(command in ("read", "submit") and domain in DOMAINS and domain in profile.get(command, []),
                "Für dieses Framework und diesen Bereich fehlt die Berechtigung")
        if command == "read":
            state = rehydrate(self.root)
            return {"version": state["version"], "records": live_records(self.root, state, domain)}
        source = {"title": request["title"], "source_text": request["text"], "submitted_by": self.operator}
        return submit(self.db, key, request["receipt"], domain, source)


def serve(console, port):
    prefix = "/" + secrets.token_urlsafe(24) + "/"

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, *_):
            return

        def respond(self, status, body, kind):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def json(self, status, payload):
            self.respond(status, json_text(payload), "application/json; charset=utf-8")

        def trusted(self):
            return self.headers.get("Host") == self.server.local_host and self.path.startswith(prefix)

        def do_GET(self):
            if not self.trusted():
                return self.json(404, {"error": "Unbekannte Adresse"})
            page = self.path[len(prefix):]
            try:
                if page == "":
                    return self.respond(200, (console.root / "shared_archive/console.html").read_bytes(),
                                        "text/html; charset=utf-8")
                if page == "model":
                    return self.json(200, console.model())
                if page == "overview":
                    with TemporaryDirectory() as directory:
                        html = Path(directory) / "overview.html"
                        console.overview(html)
                        return self.respond(200, html.read_bytes(), "text/html; charset=utf-8")
            except (AttributeError, ValueError, KeyError, TypeError, OSError, sqlite3.Error) as error:
                return self.json(400, {"error": str(error)})
            return self.json(404, {"error": "Unbekannte Ansicht"})

        def do_POST(self):
            if (not self.trusted() or self.path != prefix + "action"
                    or self.headers.get("Origin") != f"http://{self.server.local_host}"
                    or self.headers.get_content_type() != "application/json"):
                return self.json(403, {"error": "Zugriff verweigert"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                require(0 < length <= LIMIT, "Ungültige Anfragegröße")
                return self.json(200, console.handle(json.loads(self.rfile.read(length))))
            except (AttributeError, ValueError, KeyError, TypeError, OSError, sqlite3.Error, subprocess.TimeoutExpired) as error:
                return self.json(400, {"error": str(error)})

    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        server.local_host = f"127.0.0.1:{server.server_port}"
        print(f"http://{server.local_host}{prefix}", flush=True)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    private = args.private_dir.resolve()
    try:
        require(private.is_dir() and not private.is_relative_to(ROOT.resolve()) and
                not any((path / ".git").exists() for path in (private, *private.parents)),
                "Privaten Ordner außerhalb des Checkouts wählen")
        authorize(private / "clients.json", args.operator, os.environ.get("CLS_ARCHIVE_TOKEN"), "review")
        console = Console(ROOT, private, args.operator)
        console.model()
        serve(console, args.port)
        return 0
    except (AttributeError, ValueError, KeyError, TypeError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
