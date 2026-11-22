"""666TDH repo-native CI-Prüfkern (read-only, ohne zweite Runtime).

GitHub Actions kann diesen Einstieg nach gesonderter Freigabe aufrufen:
    python -B PROJECTS/666TDH/tools/ci_validate.py --expected-head <COMMIT>

Keine Netzwerkzugriffe, keine Repo- oder Child-Writes, keine Host-PASS-Behauptung.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NATIVE_ROOT = "PROJECTS/666TDH"
MINIMUM_R3_TESTS = 28
EXPECTED_CHILDREN = {"TD", "LCTS", "DTSTE", "FSE", "SHACHIVITI"}


def git(*args: str, cwd: Path = PROJECT_ROOT) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True,
                            capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()


def check_checkout(project_root: Path, repo_root: Path, head: str,
                   expected_head: str | None = None) -> None:
    """Verhindert den Test eines falschen Repositories oder veralteten Refs."""
    if project_root.resolve() != (repo_root.resolve() / NATIVE_ROOT):
        raise RuntimeError("HOLD: TDH-Projekt ist nicht im nativen Repository-Root")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise RuntimeError("HOLD: Git-HEAD ist kein vollständiger Commit-SHA")
    if expected_head is not None and head != expected_head:
        raise RuntimeError("READBACK_PENDING: erwarteter Git-HEAD weicht ab")


def check_native(result: dict, current) -> dict:
    """Wertet vorhandene native 666TDH-Rehydration aus; kein Parallelrouter."""
    if result.get("status") != "VERIFIZIERT_LOCAL":
        raise RuntimeError("HOLD: native Current-Validierung nicht bestanden")
    if result.get("native_id") != "666TRACKHUB-001" or result.get("native_release") != "v1.15.0":
        raise RuntimeError("HOLD: falsche TDH-Identität oder Native-Release")
    if set(result.get("children", [])) != EXPECTED_CHILDREN:
        raise RuntimeError("HOLD: falsche oder unvollständige Child-Registry")
    if result.get("daemon_commands") != 9:
        raise RuntimeError("HOLD: Daemon-Routen stimmen nicht überein")
    pointer = current.pointer
    if result.get("current_manifest_count") != len(pointer["files"]):
        raise RuntimeError("HOLD: Current-Manifest nicht vollständig geprüft")
    if pointer.get("authority") != "REPOSITORY_PROJECT":
        raise RuntimeError("HOLD: falsche Repo-Authority")
    if pointer.get("repo_policy_revision", {}).get("revision") != "R1" or \
            pointer.get("repo_capability_revision", {}).get("revision") != "R3":
        raise RuntimeError("HOLD: Policy oder R3-Revision nicht verifiziert")
    for token in ("FSE", "SHACHIVITI"):
        if current.registry["children"][token].get("source_identity") != "UNRESOLVED_HOLD":
            raise RuntimeError("HOLD: Source-Identity-Guard verletzt: " + token)
    if result.get("chat_host_acceptance") != "OPEN_NOT_VERIFIED":
        raise RuntimeError("HOLD: ohne Host-Nachweis darf kein Host-PASS entstehen")

    intake = pointer.get("r10_clic_intake")
    if intake is not None:
        receipt = current.document(intake["native_return_receipt"])
        audit = current.document(intake["audit_path"])
        if receipt.get("receipt_id") != "666TDH-TO-666CLIC-R10-20261122-01" or \
                receipt.get("host_accepted") is not False or \
                receipt.get("no_clic_repository_write") is not True or \
                len(audit.get("findings", [])) != 5:
            raise RuntimeError("HOLD: R10-Return-Receipt/Audit widerspricht dem Current")
        r10 = "R10_RECEIPT_NATIVE_VERIFIED_RECIPIENT_ACK_SEPARATE"
    else:
        r10 = "NOT_PRESENT"
    return {"native_release": pointer["release"],
            "capability_revision": pointer["repo_capability_revision"]["revision"],
            "manifest_sha256_bindings_verified": len(pointer["files"]),
            "children": sorted(result["children"]),
            "daemon_routes": result["daemon_commands"],
            "r10": r10,
            "chatgpt_host_acceptance": "OPEN_NOT_VERIFIED",
            "fse_external_vault": "SOURCE_VAULT_ONLY_NOT_TESTED"}


def successful_test_count(output: str, return_code: int) -> int:
    match = re.search(r"^Ran (\d+) tests? in [^\n]+$", output, re.MULTILINE)
    if return_code != 0 or match is None or re.search(r"^OK(?:\s.*)?$", output, re.MULTILINE) is None:
        raise RuntimeError("HOLD: Python-Tests fehlgeschlagen oder kein beweiskräftiger Unittest-Report")
    count = int(match.group(1))
    if count < MINIMUM_R3_TESTS:
        raise RuntimeError(f"HOLD: erwartete R3-Tests fehlen ({count} statt mindestens {MINIMUM_R3_TESTS})")
    return count


def execute(expected_head: str | None = None) -> dict:
    repo = Path(git("rev-parse", "--show-toplevel")).resolve()
    head = git("rev-parse", "HEAD", cwd=repo)
    check_checkout(PROJECT_ROOT, repo, head, expected_head)
    tracked_scope = git("status", "--porcelain", "--untracked-files=all", "--", NATIVE_ROOT, cwd=repo)
    if tracked_scope:
        raise RuntimeError("HOLD: TDH-Arbeitsbaum enthält lokale Änderungen")
    sys.path.insert(0, str(PROJECT_ROOT))
    from tools.verify_and_backup import verify
    from tdh import Current
    native = check_native(verify(), Current(PROJECT_ROOT))
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover",
                                "-s", "tests", "-p", "test_*.py", "-v"],
                               cwd=PROJECT_ROOT, env=environment,
                               capture_output=True, text=True, encoding="utf-8")
    combined = completed.stdout + "\n" + completed.stderr
    try:
        total = successful_test_count(combined, completed.returncode)
    except RuntimeError as exc:
        raise RuntimeError(str(exc) + "\n" + combined[-12000:]) from exc
    if git("status", "--porcelain", "--untracked-files=all", "--", NATIVE_ROOT, cwd=repo):
        raise RuntimeError("HOLD: Regressionslauf hat den TDH-Arbeitsbaum verändert")
    return {"status": "PASS_REPO_NATIVE_REGRESSION_NO_HOST_ASSERTION",
            "system_id": "666TRACKHUB-001", "commit_sha": head,
            "repository_scope": NATIVE_ROOT, "python_tests_passed": total,
            "remote_writes": "NONE", "child_mutations": "NONE", **native}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", help="Exakter zu prüfender HEAD (40 Hex-Zeichen)")
    args = parser.parse_args()
    try:
        print(json.dumps(execute(args.expected_head), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "HOLD", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
