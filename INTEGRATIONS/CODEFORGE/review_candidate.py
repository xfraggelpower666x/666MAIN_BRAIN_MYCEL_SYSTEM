"""Combine read-only Git scope and quality receipt checks for one candidate."""
import argparse
import json
from pathlib import Path
import subprocess

from .candidate_snapshot import candidate_snapshot
from .check_patch_scope import changed_paths, check_scope
from ..PLUGIN_CAPABILITIES.read_gate import classify


def review_candidate(checkout, base, candidate, allowed, receipt, snapshot, required_checks,
                     *, require_patch_coverage=False):
    scope = check_scope(checkout, base, candidate, allowed)
    snapshot_provenance = "CALLER_SUPPLIED"
    if snapshot is None:
        if not isinstance(receipt, dict) or receipt.get("schema") != "gate-result/v1":
            raise ValueError("gate-result/v1 expected")
        snapshot = candidate_snapshot(checkout, candidate, receipt.get("checked_paths"))
        snapshot_provenance = "CANDIDATE_GIT_BLOBS"
    quality = classify(receipt, snapshot)
    deleted = set(changed_paths(checkout, base, candidate, deletions_only=True))
    declared = set(receipt["checked_paths"])
    missing_paths = [path for path in scope["changed"] if path not in deleted and path not in declared]
    observed = {check["name"]: check["status"] for check in quality["checks"]}
    missing = sorted(set(required_checks) - observed.keys())
    status = "REVIEW_EVIDENCE_CONSISTENT"
    if scope["outside_scope"]:
        status = "OUTSIDE_SCOPE"
    elif not scope["changed"]:
        status = "NO_CHANGE"
    elif quality["outcome"] != "REPORTED_CHECKS_PASS" or missing:
        status = "QUALITY_EVIDENCE_INCOMPLETE"
    elif require_patch_coverage and missing_paths:
        status = "PATCH_PATH_COVERAGE_INCOMPLETE"
    return {
        "status": status,
        "scope": scope,
        "quality": quality,
        "missing_required_checks": missing,
        "snapshot_provenance": snapshot_provenance,
        "patch_path_coverage": {
            "required": require_patch_coverage,
            "missing_candidate_paths": missing_paths,
            "deleted_paths": [path for path in scope["changed"] if path in deleted],
        },
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
    parser.add_argument("--require-patch-coverage", action="store_true",
                        help="Require the receipt to list every changed path still in the candidate")
    args = parser.parse_args()
    try:
        result = review_candidate(
            args.checkout, args.base, args.candidate, args.allow,
            json.loads(args.receipt.read_text(encoding="utf-8")),
            args.snapshot, args.require_check,
            require_patch_coverage=args.require_patch_coverage,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "REVIEW_EVIDENCE_CONSISTENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
