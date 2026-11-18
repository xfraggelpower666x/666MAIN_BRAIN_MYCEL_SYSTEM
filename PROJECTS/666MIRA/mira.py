"""Read-only entry point for the repository-native 666MIRA chat system."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM_ID = "666MIRA-CORE-001"


def rehydrate():
    pointer = json.loads((ROOT / "CURRENT_POINTER.json").read_bytes())
    if pointer["system_id"] != SYSTEM_ID or pointer["project_root"] != "PROJECTS/666MIRA":
        raise ValueError("falsche MIRA-Identität")
    files = {}
    for name, digest in pointer["files"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or name == "CURRENT_POINTER.json":
            raise ValueError("ungültiger Current-Pfad")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"SHA-256 weicht ab: {name}")
        files[name] = content.decode("utf-8")
    registry = json.loads(files["runtime/TRIGGERS.json"])
    handoff = json.loads(files["continuity/CURRENT_HANDOFF.json"])
    if registry["system_id"] != SYSTEM_ID or handoff["system_id"] != SYSTEM_ID or not registry["direct_current_user_only"]:
        raise ValueError("MIRA-Trägerschaft widerspricht Current")
    bootstrap = [{"path": name, "content": files[name]} for name in pointer["bootstrap_order"]]
    return pointer, registry, handoff, bootstrap


def run(words, source):
    pointer, registry, handoff, bootstrap = rehydrate()
    if not words or words[0].upper() != registry["namespace"]:
        raise ValueError("direkter 666MIRA-Aufruf erforderlich")
    key = " ".join(words[1:]).upper()
    route = registry["routes"].get(key)
    if route is None:
        raise ValueError("unbekannter MIRA-Aufruf")
    result = {
        "system_id": SYSTEM_ID, "release": pointer["release"], "route": route,
        "status": "VERIFIZIERT", "evidence": "lokaler Current und SHA-256 verifiziert",
        "return_anchor": handoff["return_anchor"], "host_acceptance": handoff["state"],
    }
    if route in ("rehydrate", "sentence_mantra"):
        result["bootstrap"] = bootstrap
    if route == "resume":
        result["next_step"] = handoff["next_step"]
    if route == "governed_update":
        result.update(status="OFFEN", next_step="Ziel, Scope, Lock und frischen GitHub-HEAD im autorisierten Host prüfen.")
    if route == "sentence_mantra":
        result["source_text"] = source
        result["status"] = "OFFEN"
        result["next_step"] = ("Chat-Host: Quelle und Zielsprache klären, Framework anwenden."
                               if source and source.strip() else "Quellsatz anfordern.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trigger", nargs="+")
    parser.add_argument("--text")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.trigger, args.text), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "OFFEN", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
