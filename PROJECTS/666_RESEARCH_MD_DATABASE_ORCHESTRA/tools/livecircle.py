#!/usr/bin/env python3
"""Read-only LiveCircle for the partial 666 Research Orchestra source recovery.

This tool never declares a historical release frozen and never writes to GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "history/v1_7_1/SYSTEM_ONLY_FILE_MANIFEST_SHA256.txt"
STATE = ROOT / "state/LIVE_WORKSPACE_STATE.json"


def expected_hashes() -> dict[str, str]:
    result = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, path = line.split("  ", 1)
        if len(digest) != 64 or path in result:
            raise ValueError("Duplicate or invalid historical hash entry")
        result[path] = digest.lower()
    return result


def known_source_files() -> dict[str, pathlib.Path]:
    result = {}
    for sub in ("data/topics", "data/prompts"):
        for path in sorted((ROOT / sub).glob("*.js")):
            result[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "history/v1_7_1").iterdir():
        if path.is_file() and path.name != "SYSTEM_ONLY_FILE_MANIFEST_SHA256.txt":
            result[path.name] = path
    return result


def audit() -> dict:
    expected = expected_hashes()
    actual = known_source_files()
    verified, mismatch, unexpected = [], [], []
    for rel, path in actual.items():
        if rel not in expected:
            unexpected.append(rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() == expected[rel]:
            verified.append(rel)
        else:
            mismatch.append(rel)
    missing = sorted(set(expected) - set(actual))
    return {
        "status": "READBACK_PENDING" if (missing or mismatch or unexpected) else "VERIFIED_SOURCE_ONLY",
        "expected": len(expected), "present": len(actual), "verified": len(verified),
        "missing_count": len(missing), "mismatch": sorted(mismatch),
        "unexpected": sorted(unexpected), "missing": missing,
        "note": "This is a source inventory; runtime tests and freeze require a complete source tree.",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Research Orchestra recovery LiveCircle (read-only)")
    p.add_argument("command", choices=("status", "audit", "missing", "next"), nargs="?", default="status")
    p.add_argument("--json", action="store_true", help="Output a JSON status report")
    args = p.parse_args(argv)
    result = audit()
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if args.command == "missing":
        payload = result["missing"]
    elif args.command == "next":
        payload = state["next_steps"]
    elif args.command == "audit":
        payload = result
    else:
        payload = {"project": state["project"], "workspace": state["workspace"],
                   "historical_release": state["historical_release"],
                   "status": result["status"], "verified_originals": result["verified"],
                   "expected_originals": result["expected"], "missing_originals": result["missing_count"],
                   "freeze": "BLOCKED", "next_steps": state["next_steps"]}
    if args.json or args.command in ("audit", "missing"):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif isinstance(payload, list):
        for ix, item in enumerate(payload, 1):
            print(f"{ix}. {item}")
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 2 if args.command == "audit" and result["status"] != "VERIFIED_SOURCE_ONLY" else 0


if __name__ == "__main__":
    sys.exit(main())
