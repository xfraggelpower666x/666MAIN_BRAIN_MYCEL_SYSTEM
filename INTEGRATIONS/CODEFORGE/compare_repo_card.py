"""Compare a repository card baseline with a verified GitHub commit."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from check_patch_scope import git


def compare_repo_card(checkout, previous, current):
    for commit in (previous, current):
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
            raise ValueError("Use full Git commit IDs")
        if git(checkout, "rev-parse", "--verify", commit + "^{commit}").decode().strip() != commit:
            raise ValueError("Both IDs must name commits directly")

    # Ein flacher Checkout kann eine vorhandene Abstammung verdecken.
    ancestry = "UNCHANGED"
    if previous != current:
        shallow = git(checkout, "rev-parse", "--is-shallow-repository").strip() == b"true"
        try:
            git(checkout, "merge-base", "--is-ancestor", previous, current)
        except subprocess.CalledProcessError as error:
            if error.returncode != 1:
                raise
            ancestry = "UNKNOWN" if shallow else "DIVERGED"
        else:
            ancestry = "FAST_FORWARD"

    raw = git(
        checkout, "diff", "--no-ext-diff", "--ignore-submodules=none",
        "--name-status", "-z", "--find-renames", "-l0", previous, current, "--",
    )
    fields = iter(raw.decode("utf-8", "surrogateescape").split("\0")[:-1])
    changes = []
    statuses = {"A": "NEW", "D": "REMOVED", "M": "MODIFIED", "T": "MODIFIED"}
    for code in fields:
        path = next(fields)
        if code.startswith("R"):
            changes.append({"status": "RENAMED", "previous_path": path, "path": next(fields)})
        else:
            changes.append({"status": statuses.get(code, "UNKNOWN"), "path": path})
    return {"previous": previous, "current": current, "ancestry": ancestry, "changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--current", required=True)
    args = parser.parse_args()
    try:
        report = compare_repo_card(args.checkout, args.previous, args.current)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
    return 1 if report["ancestry"] in ("DIVERGED", "UNKNOWN") else 0


if __name__ == "__main__":
    raise SystemExit(main())
