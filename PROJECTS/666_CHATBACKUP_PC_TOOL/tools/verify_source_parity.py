#!/usr/bin/env python3
"""Non-destructive file/SHA parity verifier for the ChatBackup source transition.

Usage:
    python tools/verify_source_parity.py BASE_SOURCE_DIR INTEGRATED_SOURCE_DIR

This does not execute application code or alter files. It rejects any missing
baseline file; intentionally changed files must be reviewed separately.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

IGNORE = {"__pycache__", ".pytest_cache", "node_modules", ".git", "dist", "build"}


def inventory(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise ValueError(f"Missing source directory: {root}")
    found: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(piece in IGNORE for piece in path.relative_to(root).parts):
            continue
        name = path.relative_to(root).as_posix()
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        found[name] = digest.hexdigest()
    return found


def compare(base: Path, candidate: Path) -> dict:
    old, new = inventory(base), inventory(candidate)
    names = old.keys() & new.keys()
    return {
        "baseline_count": len(old),
        "candidate_count": len(new),
        "missing": sorted(old.keys() - new.keys()),
        "added": sorted(new.keys() - old.keys()),
        "modified": sorted(name for name in names if old[name] != new[name]),
        "unchanged_count": sum(old[name] == new[name] for name in names),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        report = compare(Path(sys.argv[1]), Path(sys.argv[2]))
    except (ValueError, OSError) as exc:
        print(f"VERIFY ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
