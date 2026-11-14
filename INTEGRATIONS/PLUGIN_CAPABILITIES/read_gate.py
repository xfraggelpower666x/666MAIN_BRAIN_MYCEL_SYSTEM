"""Classify a local gate-result/v1 receipt without running the reported commands."""
import argparse
import json
from pathlib import Path


def classify(receipt, expected_snapshot):
    if not isinstance(receipt, dict) or receipt.get("schema") != "gate-result/v1":
        raise ValueError("gate-result/v1 expected")
    status = receipt.get("status")
    digest = receipt.get("snapshot_digest")
    checks = receipt.get("checks")
    paths = receipt.get("checked_paths")
    errors = receipt.get("errors")
    findings = receipt.get("findings")
    versions = receipt.get("command_versions")
    elapsed = receipt.get("elapsed_ms")
    truncated = receipt.get("output_truncated")
    if (status not in ("pass", "fail", "timeout", "error")
            or not isinstance(digest, str) or not digest
            or not isinstance(checks, list)
            or not isinstance(paths, list) or not all(isinstance(p, str) for p in paths)
            or not isinstance(errors, list) or not isinstance(findings, list)
            or not isinstance(versions, dict) or type(elapsed) is not int or elapsed < 0
            or type(truncated) is not bool):
        raise ValueError("Invalid receipt fields")
    names = set()
    results = []
    incomplete = not checks or not paths or truncated or bool(errors)
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Invalid check")
        name, observed = check.get("name"), check.get("status")
        timed_out, clipped = check.get("timed_out"), check.get("output_truncated")
        argv, duration = check.get("argv"), check.get("elapsed_ms")
        if (not isinstance(name, str) or not name or name in names
                or observed not in ("pass", "fail", "timeout", "missing", "error", "skipped")
                or type(timed_out) is not bool or type(clipped) is not bool
                or not isinstance(argv, list) or not all(isinstance(arg, str) for arg in argv)
                or type(duration) is not int or duration < 0):
            raise ValueError("Invalid or duplicate check")
        names.add(name)
        incomplete |= timed_out or clipped or observed != "pass" or check.get("exit_code") not in (None, 0)
        results.append({"name": name, "status": observed})
    changed = receipt.get("snapshot_changed", False)
    after = receipt.get("snapshot_digest_after")
    if type(changed) is not bool or (after is not None and not isinstance(after, str)):
        raise ValueError("Invalid snapshot fields")
    if digest != expected_snapshot or changed or (after is not None and after != digest):
        outcome = "SNAPSHOT_MISMATCH"
    elif status != "pass":
        outcome = "REPORTED_" + status.upper()
    elif incomplete:
        outcome = "PARTIAL"
    else:
        outcome = "REPORTED_CHECKS_PASS"
    return {"outcome": outcome, "reported_status": status, "checks": results,
            "checked_path_count": len(paths), "finding_count": len(findings)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--snapshot", required=True, help="Expected project snapshot digest")
    args = parser.parse_args()
    try:
        report = classify(json.loads(args.receipt.read_text(encoding="utf-8")), args.snapshot)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
    return 0 if report["outcome"] == "REPORTED_CHECKS_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
