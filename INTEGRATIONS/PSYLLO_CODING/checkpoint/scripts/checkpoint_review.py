"""Prüft einen CodeForge-v1-Checkpoint lesend gegen eine vorgeprüfte Bindung."""

import argparse
from collections import Counter
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path
import re
import subprocess

BINDING_KEYS = ("project", "lineage_id", "base_commit", "scope")
STATES = {"OFFEN", "PARTIAL", "BLOCKIERT", "VERIFIZIERT", "CONFLICT_QUARANTINE"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def review(checkpoint, binding, confirmed_completed):
    if not isinstance(checkpoint, dict) or not isinstance(binding, dict):
        raise ValueError("Checkpoint und Projektbindung müssen JSON-Objekte sein.")
    if (type(checkpoint.get("schema_version")) is not int or checkpoint["schema_version"] != 1
            or checkpoint.get("example") is not False):
        raise ValueError("Erwartet wird ein tatsächlicher Checkpoint mit Schema-Version 1.")
    if not all(nonempty(binding.get(key)) for key in BINDING_KEYS):
        raise ValueError("Die geprüfte Projektbindung ist unvollständig.")
    if not re.fullmatch(r"[0-9a-f]{40}", binding["base_commit"]):
        raise ValueError("base_commit muss ein vollständiger Git-Commit sein.")
    mismatches = [key for key in BINDING_KEYS if binding[key] != checkpoint.get(key)]
    if mismatches:
        return {"status": "CONFLICT_QUARANTINE", "binding_mismatches": mismatches,
                "candidates": [], "strands": {}}
    strands = checkpoint.get("strands")
    if not isinstance(strands, list) or not strands:
        raise ValueError("Der Checkpoint braucht mindestens einen Strang.")
    if not all(isinstance(item, dict) and nonempty(item.get("id")) for item in strands):
        raise ValueError("Jeder Strang braucht eine nichtleere ID.")
    occurrences = Counter(item["id"] for item in strands)
    rows = {item["id"]: item for item in strands}
    if set(confirmed_completed) - rows.keys():
        raise ValueError("Unbekannte ID unter bestätigten Abschlüssen.")

    outcomes = {}
    topology = TopologicalSorter()
    for strand_id, item in rows.items():
        dependencies = item.get("depends_on")
        status = item.get("status")
        topology.add(strand_id)
        if occurrences[strand_id] > 1:
            outcomes[strand_id] = "DUPLICATE_ID"
        elif (not isinstance(dependencies, list) or not all(map(nonempty, dependencies))
              or len(set(dependencies)) != len(dependencies)
              or not isinstance(status, str) or status not in STATES
              or not nonempty(item.get("return_anchor"))):
            outcomes[strand_id] = "INVALID_STRAND"
        elif set(dependencies) - rows.keys():
            outcomes[strand_id] = "UNKNOWN_PREDECESSOR"
        else:
            topology.add(strand_id, *dependencies)

    try:
        topology.prepare()
    except CycleError:
        # Unabhängige Stränge bleiben auch bei Zyklen auflösbar.
        pass
    while topology.is_active():
        for strand_id in topology.get_ready():
            if strand_id not in outcomes:
                outcomes[strand_id] = classify(strand_id, rows[strand_id], outcomes, confirmed_completed)
            topology.done(strand_id)
    for strand_id in rows:
        outcomes.setdefault(strand_id, "CYCLE_OR_DEPENDENT")
    candidates = [
        {"id": strand_id, "return_anchor": item["return_anchor"]}
        for strand_id, item in rows.items() if outcomes[strand_id] == "CANDIDATE"
    ]
    needs_review = any(result not in {"CANDIDATE", "CONFIRMED_COMPLETE"} for result in outcomes.values())
    return {"status": "PARTIAL" if needs_review else "STRUCTURALLY_REVIEWED",
            "binding_mismatches": [], "candidates": candidates, "strands": outcomes}


def classify(strand_id, item, outcomes, confirmed_completed):
    if item.get("write_outcome") in ("unknown", "readback_pending"):
        return "READBACK_PENDING"
    if item["status"] in {"BLOCKIERT", "CONFLICT_QUARANTINE"}:
        return item["status"]
    if any(outcomes[parent] != "CONFIRMED_COMPLETE" for parent in item["depends_on"]):
        return "WAITING_FOR_PREDECESSOR"
    if item["status"] == "VERIFIZIERT":
        evidence = item.get("evidence")
        if strand_id in confirmed_completed and isinstance(evidence, list) and evidence and all(map(nonempty, evidence)):
            return "CONFIRMED_COMPLETE"
        return "COMPLETION_UNCONFIRMED"
    return "CANDIDATE"


def git(repo, *args, allowed=(0,)):
    result = subprocess.run(["git", "-C", str(repo), "--no-replace-objects", "--no-optional-locks", *args],
                            capture_output=True, timeout=30, check=False)
    if result.returncode not in allowed:
        raise ValueError(f"Git-Nachweis fehlt für {args[0]} (Exit {result.returncode}).")
    return result


def worktree_paths(repo):
    # NUL-Trennung erhält Leerzeichen und Zeilenumbrüche in Git-Pfaden.
    output = git(repo, "status", "--porcelain=v1", "-z", "--no-renames",
                 "--untracked-files=all", "--ignore-submodules=none").stdout
    paths = {}
    for entry in output.split(b"\0"):
        if not entry:
            continue
        if len(entry) < 4 or entry[2:3] != b" ":
            raise ValueError("Nicht unterstützter Git-Arbeitsbaumstatus.")
        status = entry[:2].decode("ascii")
        path = entry[3:].decode("utf-8", "surrogateescape")
        if status in {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}:
            origins = ["conflict"]
        elif status == "??":
            origins = ["untracked"]
        else:
            origins = [layer for marker, layer in zip(status, ("index", "worktree")) if marker != " "]
        paths[path] = origins
    return paths


def binding_conflict(reason):
    return {"status": "CONFLICT_QUARANTINE", "binding_mismatches": [reason],
            "candidates": [], "strands": {}}


def review_revision(checkpoint, binding, confirmed_completed, repo, *, include_worktree=False):
    """Revalidiert einen Checkpoint gegen zwei belegte, lokale Git-Commits."""
    current = binding.get("base_commit")
    previous = checkpoint.get("base_commit")
    for commit in (current, previous):
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("Vollständige Git-Commit-IDs erforderlich.")
    former_binding = {**binding, "base_commit": previous}
    original = review(checkpoint, former_binding, confirmed_completed)
    if original["binding_mismatches"]:
        return original
    for commit in {previous, current}:
        git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    ancestry = git(repo, "merge-base", "--is-ancestor", previous, current, allowed=(0, 1))
    if ancestry.returncode == 1:
        return binding_conflict("commit_ancestry")
    local_paths = {}
    if include_worktree:
        if git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip() != current:
            return binding_conflict("worktree_head")
        local_paths = worktree_paths(repo)
        if git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip() != current:
            return binding_conflict("worktree_head")
    diff = git(repo, "diff", "--no-ext-diff", "--no-renames", "--name-only", "-z",
               previous, current, "--").stdout
    changed = {item.decode("utf-8", "surrogateescape") for item in diff.split(b"\0") if item}
    invalid = {}
    updated = []
    for strand in checkpoint["strands"]:
        identifier = strand["id"]
        target = dict(strand)
        updated.append(target)
        if original["strands"][identifier] in {"DUPLICATE_ID", "INVALID_STRAND",
                                               "UNKNOWN_PREDECESSOR", "CYCLE_OR_DEPENDENT"}:
            continue
        if strand.get("write_outcome") in ("unknown", "readback_pending"):
            invalid[identifier] = {"next": "READBACK", "changed_paths": []}
        elif previous != current or local_paths:
            paths = strand.get("contract_paths")
            if not isinstance(paths, list) or not paths or not all(
                nonempty(path) and not path.startswith("/") and "\\" not in path
                and ":" not in path and all(part not in ("", ".", "..") for part in path.split("/"))
                for path in paths
            ):
                invalid[identifier] = {"next": "BIND_EVIDENCE", "changed_paths": []}
            else:
                impacted = sorted(path for path in changed | local_paths.keys() if any(
                    path == watch or path.startswith(watch + "/") for watch in paths
                ))
                if impacted:
                    has_conflict = any("conflict" in local_paths.get(path, []) for path in impacted)
                    invalid[identifier] = {
                        "next": "RESOLVE_CONFLICT" if has_conflict else "REVALIDATE",
                        "changed_paths": impacted,
                    }
        if identifier in invalid:
            target["status"] = "BLOCKIERT"
    reviewed = review({**checkpoint, "base_commit": current, "strands": updated},
                      binding, set(confirmed_completed) - invalid.keys())
    reviewed["basis"] = {"checkpoint": previous, "current": current, "kind": "committed_git_diff"}
    if include_worktree:
        reviewed["basis"]["kind"] = "committed_git_diff_and_worktree_status"
        reviewed["worktree"] = {"changed_path_count": len(local_paths),
                                "relevant_paths": {path: local_paths[path]
                                                   for path in sorted(local_paths)
                                                   if any(path in row["changed_paths"]
                                                          for row in invalid.values())}}
    reviewed["recovery"] = invalid
    return reviewed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("binding", type=Path, help="Aus unabhängig geprüfter Projektquelle")
    parser.add_argument("--confirmed-complete", action="append", default=[], metavar="STRAND_ID")
    parser.add_argument("--git-repo", type=Path, help="Lesender Abgleich der bestätigten Git-Basis")
    parser.add_argument("--include-worktree", action="store_true",
                        help="Index und Arbeitsbaum des bestätigten lokalen HEAD mitprüfen")
    args = parser.parse_args()
    if args.include_worktree and args.git_repo is None:
        parser.error("--include-worktree erfordert --git-repo")
    try:
        checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        binding = json.loads(args.binding.read_text(encoding="utf-8"))
        confirmed = set(args.confirmed_complete)
        if not isinstance(checkpoint, dict) or not isinstance(binding, dict):
            raise ValueError("Checkpoint und Projektbindung müssen JSON-Objekte sein.")
        result = (review_revision(checkpoint, binding, confirmed, args.git_repo,
                                  include_worktree=args.include_worktree)
                  if args.git_repo is not None else review(checkpoint, binding, confirmed))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
