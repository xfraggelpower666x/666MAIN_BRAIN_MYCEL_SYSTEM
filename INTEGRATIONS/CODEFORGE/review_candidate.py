"""Combine read-only Git scope and quality receipt checks for one candidate."""
import argparse
import json
from pathlib import Path
import subprocess

from .candidate_snapshot import candidate_snapshot
from .check_patch_scope import check_scope
from ..PLUGIN_CAPABILITIES.read_gate import classify


def review_candidate(checkout, base, candidate, allowed, receipt, snapshot, required_checks):
    scope = check_scope(checkout, base, candidate, allowed)
    snapshot_provenance = "CALLER_SUPPLIED"
    if snapshot is None:
        if not isinstance(receipt, dict) or receipt.get("schema") != "gate-result/v1":
            raise ValueError("gate-result/v1 expected")
        snapshot = candidate_snapshot(checkout, candidate, receipt.get("checked_paths"))
        snapshot_provenance = "CANDIDATE_GIT_BLOBS"
    quality = classify(receipt, snapshot)
    observed = {check["name"]: check["status"] for check in quality["checks"]}
    missing = sorted(set(required_checks) - observed.keys())
    status = "REVIEW_EVIDENCE_CONSISTENT"
    if scope["outside_scope"]:
        status = "OUTSIDE_SCOPE"
    elif not scope["changed"]:
        status = "NO_CHANGE"
    elif quality["outcome"] != "REPORTED_CHECKS_PASS" or missing:
        status = "QUALITY_EVIDENCE_INCOMPLETE"
    return {
        "status": status,
        "scope": scope,
        "quality": quality,
        "missing_required_checks": missing,
        "snapshot_provenance": snapshot_provenance,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--allow", action="append", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    snapshot_mode = parser.add_mutually_exclusive_group(required=True)
    snapshot_mode.add_argument("--snapshot", help="Expected digest supplied by the caller")
    snapshot_mode.add_argument("--snapshot-from-candidate", action="store_true",
                               help="Derive the digest from committed regular files")
    parser.add_argument("--require-check", action="append", required=True)
    args = parser.parse_args()
    try:
        result = review_candidate(
            args.checkout, args.base, args.candidate, args.allow,
            json.loads(args.receipt.read_text(encoding="utf-8")),
            args.snapshot, args.require_check,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "REVIEW_EVIDENCE_CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
