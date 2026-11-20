"""Repo-nativer Einstieg für 666TDH. Benötigt nur Python 3.10+."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

from runtime.facets.lifecycle import (FacetError, validate_bindings, profile_state,
                                      scoped_continuity, checkpoint_template)
from runtime.ui.view_model import build_view_model
from runtime.ui.render_html import render_html


SYSTEM_ID = "666TRACKHUB-001"
NAMESPACE = "666TDH"


class CurrentError(Exception):
    """Der verifizierte Current kann nicht aufgelöst werden."""


def unique_json(raw: bytes) -> dict:
    """Kontroll-Dateien mit doppelten JSON-Schlüsseln fail-closed ablehnen."""
    def unique(pairs):
        obj = dict(pairs)
        if len(obj) != len(pairs):
            raise CurrentError("HOLD: Doppelter JSON-Schlüssel in Current-Steuerdaten")
        return obj
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise CurrentError("HOLD: Current-Steuerdaten müssen JSON-Objekte sein")
    return data


class Current:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.pointer = unique_json(self.read("CURRENT_POINTER.json"))
        if self.pointer["system_id"] != SYSTEM_ID or self.pointer["namespace"] != NAMESPACE:
            raise CurrentError("Current gehört zu einem anderen System.")
        if self.pointer["authority"] != "REPOSITORY_PROJECT":
            raise CurrentError("Der Current besitzt keine Repo-Projektautorität.")
        self.hashes = self.pointer["files"]
        self.registry = self.document("runtime/REGISTRY.json")
        self.routes = self.document("runtime/TRIGGERS.json")
        self.handoff = self.document("continuity/CURRENT_HANDOFF.json")
        self.subfacet_bindings = self.document("runtime/facets/SUBFACET_BINDINGS.json")
        try:
            validate_bindings(self.subfacet_bindings, self.registry, SYSTEM_ID)
        except FacetError as exc:
            raise CurrentError(str(exc)) from exc
        if self.registry["system_id"] != SYSTEM_ID or self.handoff["system_id"] != SYSTEM_ID:
            raise CurrentError("Registry oder Handoff gehört zu einem anderen System.")
        if self.handoff["source_release"] != self.pointer["release"]:
            raise CurrentError("Handoff und Current verwenden verschiedene Releases.")
        if self.handoff["runtime_authority"] != "NONE":
            raise CurrentError("Handoff darf keine Laufzeitautorität besitzen.")

    def read(self, relative: str) -> bytes:
        path = PurePosixPath(relative)
        if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in relative:
            raise CurrentError("Ungültiger Current-Pfad.")
        file = self.root.joinpath(*path.parts)
        if file.resolve(strict=True) != file or not file.is_file():
            raise CurrentError(f"Ungültiges Current-Objekt: {relative}")
        return file.read_bytes()

    def verified(self, relative: str) -> bytes:
        expected = self.hashes.get(relative)
        if expected is None:
            raise CurrentError(f"Datei fehlt im Current-Manifest: {relative}")
        raw = self.read(relative)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise CurrentError(f"SHA-256 stimmt nicht überein: {relative}")
        return raw

    def document(self, relative: str) -> dict:
        return unique_json(self.verified(relative))

    def parse(self, message: str) -> tuple[str | None, str]:
        prefix, gap, suffix = message.strip().partition(" ")
        if prefix != NAMESPACE or not gap:
            raise CurrentError("Direkten 666TDH-Trigger eingeben. 666TDH HELP zeigt die Befehle.")
        if suffix in self.routes["root"]:
            return None, suffix
        token, _, action = suffix.partition(" ")
        if token == "DAEMON" and action in self.routes.get("daemon", []):
            # Integrierter Hub-Unterbefehl, kein zweiter Controller/Router.
            return None, f"DAEMON {action}"
        if token in self.registry["children"] and action in self.routes["child"]:
            return token, action
        raise CurrentError("Der Trigger oder Branch-Token ist in der aktuellen Registry nicht registriert.")

    def execute(self, message: str, include_bootstrap: bool = False,
                checkpoint: dict | None = None) -> dict:
        token, action = self.parse(message)
        # Gehärteter Einstieg. Nur Repo-Current-Dateien sind Teil der Rehydration.
        verified = {path: self.verified(path) for path in self.hashes}
        child = self.registry["children"].get(token)
        current_state = self.pointer["state"]
        bootstrap = self.pointer["bootstrap_order"][:]
        profile = self.subfacet_bindings["child_profiles"].get(token) if child else None
        if child:
            self.verify_child(token, child)
            bootstrap += child["bootstrap"]
            bootstrap.append(profile["visual_adapter_path"])
        if action in {"DASHBOARD", "VISUAL"}:
            bootstrap += self.registry["visual_bootstrap"]
        result = {
            "system_id": SYSTEM_ID,
            "release": self.pointer["release"],
            "repository_state": current_state,
            "verification": "VERIFIED_LOCAL_CURRENT",
            "files_verified": len(verified),
            "action": action,
            "selected_branch": token,
            "target": child["system_id"] if child else SYSTEM_ID,
            "summary": self.routes["descriptions"][action],
            "bootstrap_order": bootstrap,
        }
        if child:
            result["child"] = {key: value for key, value in child.items() if key != "bootstrap"}
            result["subfacet"] = profile_state(token, profile)
        if action in {"SYSTEMSTART", "HELP", "STATUS", "DASHBOARD", "VISUAL", "HOST RECOVERY", "DAEMON STATUS", "DAEMON MENU", "DAEMON HELP", "DAEMON BACK"}:
            result["commands"] = self.commands(token)
        if action in {"SYSTEMSTART", "HELP", "STATUS"} and token is None:
            result["hub_commands"] = [f"{NAMESPACE} {route}" for route in self.routes["root"]]
        if checkpoint is not None and action not in {"WEITER", "NEW CHAT", "SYSTEMSTART", "DAEMON CONTINUE", "DAEMON WEITER", "DAEMON NEW CHAT"}:
            raise CurrentError("HOLD: Checkpoint nur für Rehydration/WEITER/NEW CHAT")
        continuity = None
        if action in {"WEITER", "NEW CHAT", "HOST RECOVERY", "DAEMON CONTINUE", "DAEMON WEITER", "DAEMON NEW CHAT"} or checkpoint is not None:
            try:
                continuity = scoped_continuity(
                    checkpoint, pointer_sha256=hashlib.sha256(self.read("CURRENT_POINTER.json")).hexdigest(),
                    release=self.pointer["release"], target_system_id=child["system_id"] if child else SYSTEM_ID,
                    branch_token=token, provider_handoff=self.handoff)
            except FacetError as exc:
                raise CurrentError(str(exc)) from exc
            if profile and continuity.get("development_position") is not None and \
                    continuity["development_position"] not in profile["local_lifecycle"]:
                raise CurrentError("HOLD: Entwicklungsposition gehört nicht zum Child-Sub-LiveCircle")
            result["continuity"] = continuity
        if action in {"NEW CHAT", "DAEMON NEW CHAT"}:
            result["checkpoint_template"] = checkpoint_template(
                pointer_raw=self.read("CURRENT_POINTER.json"), release=self.pointer["release"],
                target_system_id=child["system_id"] if child else SYSTEM_ID, branch_token=token)
            selector = f"{NAMESPACE} {token}" if token else NAMESPACE
            result["next_chat_trigger"] = f"{selector} SYSTEMSTART"
        if action in {"DASHBOARD", "VISUAL"}:
            result["visual_host_acceptance"] = "OPEN_NOT_VERIFIED"
        if action == "UPDATE":
            result["publication"] = {
                "status": "PREFLIGHT_VERIFIED",
                "target": "666MAIN_BRAIN:PROJECTS/666TDH",
                "procedure": "runtime/LIVECIRCLE.md",
                "pointer_last": True,
            }
        result["intelligent_ui"] = build_view_model(
            registry=self.registry, routes=self.routes, token=token, release=self.pointer["release"],
            profile=profile, continuity=continuity, pointer_state=current_state,
            files_verified=len(verified))
        result["daemon"] = result["intelligent_ui"]["companion"]
        if action.startswith("DAEMON "):
            # Keine Daemon-Writes: alle Aktionen bleiben an den geprüften Hub gebunden.
            verb = action.split(" ", 1)[1]
            result["daemon_commands"] = [f"{NAMESPACE} DAEMON {name}" for name in self.routes["daemon"]]
            result["daemon_operation"] = {
                "operation": verb, "authority": "NONE", "scope": "HUB",
                "persistence": "NONE", "selected_child": None,
                "status": "SESSION_ONLY_DISPLAY_MUTED" if verb == "STOP" else "READ_ONLY_RESPONSE",
            }
            if verb == "NEXT":
                result["next_safe_action"] = result["daemon"]["next_safe_action"]
                result["suggested_command"] = result["daemon"]["suggested_command"]
            if verb == "STOP":
                result["daemon"] = {**result["daemon"], "state": "SESSION_ONLY_DISPLAY_MUTED",
                                    "autoactive": True}
        if include_bootstrap:
            result["bootstrap"] = {path: verified[path].decode("utf-8-sig") for path in dict.fromkeys(bootstrap)}
        return result

    def verify_child(self, branch: str, child: dict) -> None:
        pointer = self.document(child["current_path"])
        resolved = (pointer["branch_token"], pointer["system_id"], pointer["version"])
        expected = (branch, child["system_id"], child["version"])
        if pointer["parent_system_id"] != SYSTEM_ID or resolved != expected:
            raise CurrentError(f"Child-Current stimmt nicht mit der Registry überein: {branch}")
        if child["bootstrap"] != [child["current_path"], *pointer["bootstrap"]]:
            raise CurrentError(f"Child-Bootstrap stimmt nicht mit der Registry überein: {branch}")

    def continuity(self, branch: str | None) -> dict:
        # Der Handoff ergänzt ausschließlich die vom Nutzer gewählte Zielroute.
        handoff = self.handoff
        if handoff["target_branch"] != branch:
            return {"status": "NO_BOUND_HANDOFF", "open_step": None}
        return {"status": handoff["status"], "open_step": handoff["open_step"], "handoff_id": handoff["handoff_id"]}

    def commands(self, branch: str | None) -> list[dict]:
        registry = self.registry["children"]
        tokens = [branch] if branch else registry
        commands = [
            {"branch": token, "name": registry[token]["name"], "command": f"{NAMESPACE} {token} SYSTEMSTART"}
            for token in tokens
        ]
        if branch:
            commands.extend({"branch": branch, "command": f"{NAMESPACE} {branch} {action}"} for action in self.routes["child"] if action != "SYSTEMSTART")
        return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="666TDH Current rehydrieren und einen direkten Trigger auswerten.")
    parser.add_argument("trigger", nargs="+", help="Zum Beispiel 666TDH TD SYSTEMSTART")
    parser.add_argument("--bootstrap", action="store_true", help="Verifizierte Bootstrap-Texte im JSON ausgeben")
    parser.add_argument("--checkpoint", type=Path, help="Revisionsgebundener lokaler Handoff für WEITER/NEW CHAT")
    parser.add_argument("--html", type=Path, help="Offline-HTML-Ansicht außerhalb des Repo-Roots exportieren")
    args = parser.parse_args()
    try:
        root = Path(__file__).parent
        checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8")) if args.checkpoint else None
        result = Current(root).execute(" ".join(args.trigger), args.bootstrap, checkpoint)
        if args.html:
            if args.html.resolve().is_relative_to(root.resolve()) or args.html.suffix.lower() != ".html":
                raise CurrentError("HOLD: HTML-Ausgabe nur als .html außerhalb des System-Roots")
            args.html.parent.mkdir(parents=True, exist_ok=True)
            args.html.write_text(render_html(result["intelligent_ui"]), encoding="utf-8")
            result["html_export"] = str(args.html)
    except (CurrentError, OSError, KeyError, TypeError, UnicodeError, ValueError) as exc:
        print(json.dumps({"status": "HOLD", "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
