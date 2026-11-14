"""Check a Git commit range against an explicit repository-relative path scope."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


def git(checkout, *arguments):
    result = subprocess.run(
        ["git", "-C", str(checkout), *arguments], capture_output=True, check=True
    )
    return result.stdout


def scope_entry(value):
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or str(path) != value:
        raise ValueError(f"Invalid repository-relative scope: {value!r}")
    return value


def changed_paths(checkout, base, candidate, *, deletions_only=False):
    filters = ("--diff-filter=D",) if deletions_only else ()
    raw = git(
        checkout, "diff", "--no-ext-diff", "--no-renames", "--ignore-submodules=none",
        "--name-only", "-z", *filters, base, candidate, "--",
    )
    return [path.decode("utf-8", "surrogateescape") for path in raw.split(b"\0") if path]


def check_scope(checkout, base, candidate, allowed):
    for commit in (base, candidate):
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
            raise ValueError("Use full Git commit IDs")
        if git(checkout, "rev-parse", "--verify", commit + "^{commit}").decode().strip() != commit:
            raise ValueError("Both IDs must name commits directly")
    git(checkout, "merge-base", "--is-ancestor", base, candidate)
    allowed = tuple(scope_entry(value) for value in allowed)
    changed = changed_paths(checkout, base, candidate)
    outside = [
        path for path in changed
        if not any(path == entry or path.startswith(entry + "/") for entry in allowed)
    ]
    return {"base": base, "candidate": candidate, "changed": changed,
            "outside_scope": outside, "status": "OUTSIDE_SCOPE" if outside else "IN_SCOPE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--allow", action="append", required=True)
    args = parser.parse_args()
    try:
        report = check_scope(args.checkout, args.base, args.candidate, args.allow)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
    return 1 if report["outside_scope"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
