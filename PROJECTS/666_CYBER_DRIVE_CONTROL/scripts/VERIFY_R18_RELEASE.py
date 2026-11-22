#!/usr/bin/env python3
"""Fail-closed R18 Git source release check. Never alters files or Git state."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
SOURCE = PROJECT / "r18-legacy"
SUBTREE = "PROJECTS/666_CYBER_DRIVE_CONTROL/r18-legacy"
EXPECTED_FILE = PROJECT / "docs" / "R18_ORIGINAL_GIT_BLOBS.json"


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"git {args[0]} failed: {proc.stderr[:600]}")
    return proc.stdout.strip()


def verify() -> dict:
    expected = json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))
    if len(expected) != 186:
        raise RuntimeError("Expected exact 186-file manifest")
    if not (REPO / ".git").exists():
        raise RuntimeError("Not a live Git checkout")
    if Path(git("rev-parse", "--show-toplevel")).resolve() != REPO:
        raise RuntimeError("Unexpected Git root")
    if git("branch", "--show-current") != "666MAIN_BRAIN":
        raise RuntimeError("Wrong branch: expected 666MAIN_BRAIN")
    if not SOURCE.is_dir():
        raise RuntimeError("R18 source directory missing")
    actual = {}
    for entry in git("ls-tree", "-r", "HEAD", "--", SUBTREE).splitlines():
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode, kind, blob_sha = meta.split(" ")
        if kind != "blob" or mode not in ("100644", "100755"):
            raise RuntimeError("Unexpected git entry: " + path)
        if not path.startswith(SUBTREE + "/"):
            raise RuntimeError("Git entry outside R18 subtree")
        relative = path[len(SUBTREE) + 1:]
        actual[relative] = blob_sha
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        mismatch = sorted(p for p in set(expected) & set(actual) if expected[p] != actual[p])
        raise RuntimeError(f"Git source mismatch: missing={missing[:4]}, extra={extra[:4]}, changed={mismatch[:4]}")
    for rel in expected:
        if not (SOURCE / rel).is_file():
            raise RuntimeError("Missing working-tree source: " + rel)
    dirty = git("status", "--porcelain", "--", SUBTREE)
    if dirty:
        raise RuntimeError("R18 source working tree has uncommitted changes")
    return {"status": "VERIFIED", "files": 186, "branch": "666MAIN_BRAIN",
            "head": git("rev-parse", "HEAD")}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), sort_keys=True))
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("BUILD_BLOCKED: " + str(error), file=sys.stderr)
        sys.exit(2)
