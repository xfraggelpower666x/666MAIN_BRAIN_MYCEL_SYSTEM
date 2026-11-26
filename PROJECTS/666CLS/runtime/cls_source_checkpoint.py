"""CLS-native read-only verification of an isolated CURES source checkpoint.

Never imports, executes, or promotes any candidate module. All source paths must
remain under the existing immutable candidate root.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

SOURCE_ROOT = "isolated_candidates/CURES_R08/source"
RECEIPT = "isolated_candidates/CURES_R08/PUBLICATION_RECEIPT.json"
BOUNDARY = "isolated_candidates/CURES_R08/BOUNDARY.json"
EXPECTED_ID = "CURES_R08_ISOLATED_FULL_SOURCE_20261125"
EXPECTED_OWNER = "666PFS-CURES-001"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_source_checkpoint(root: Path, pointer: dict) -> dict:
    """Fail-closed read-only manifest and ownership verification.

    This checks local source bytes, not Git remote reachability or plugin-host
    execution. Prior native Current verification is performed by the caller.
    """
    checkpoint = pointer.get("source_publication_checkpoint")
    if checkpoint is None:
        return {"status": "NOT_DECLARED"}  # backward-compatible older CLS pointers
    if not isinstance(checkpoint, dict):
        raise ValueError("CLS source checkpoint invalid")
    if (checkpoint.get("id") != EXPECTED_ID
            or checkpoint.get("role") != "IMMUTABLE_CANDIDATE_SOURCE_NOT_NATIVE_RUNTIME"
            or checkpoint.get("source_root") != SOURCE_ROOT
            or checkpoint.get("receipt") != RECEIPT
            or checkpoint.get("boundary") != BOUNDARY
            or checkpoint.get("cures_owner") != EXPECTED_OWNER
            or checkpoint.get("autoload") is not False
            or checkpoint.get("runtime_promotion") is not False
            or checkpoint.get("pfs_hold_preserved") is not True
            or checkpoint.get("foreign_writes") is not False
            or checkpoint.get("host_acceptance") is not False):
        raise ValueError("CLS source checkpoint authority/boundary mismatch")
    candidate = (root / SOURCE_ROOT).resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    if not candidate.is_relative_to(root_resolved) or not candidate.is_dir():
        raise ValueError("CLS candidate root escaped native project")
    receipt_path = (root / RECEIPT).resolve(strict=True)
    boundary_path = (root / BOUNDARY).resolve(strict=True)
    for path in (receipt_path, boundary_path):
        if not path.is_relative_to(root_resolved) or not path.is_file():
            raise ValueError("CLS candidate checkpoint path invalid")
    if (checkpoint.get("receipt_blob") != _git_blob(receipt_path)
            or checkpoint.get("boundary_blob") != _git_blob(boundary_path)):
        raise ValueError("CLS checkpoint receipt/boundary Git blob mismatch")
    boundary = _load_json(boundary_path)
    receipt = _load_json(receipt_path)
    if (boundary.get("owner") != "666CLS-CORE-001"
            or boundary.get("current_owner") != EXPECTED_OWNER
            or boundary.get("executable") is not False
            or boundary.get("autoload") is not False
            or boundary.get("native_promotion") is not False
            or boundary.get("cls_integration") != "REFERENCE_ONLY"
            or receipt.get("owner") != "666CLS-CORE-001"
            or receipt.get("source_git_tree_sha") != checkpoint.get("source_tree_sha")
            or receipt.get("archive_file_entries") != checkpoint.get("source_files")
            or receipt.get("manifest_bound_files") != checkpoint.get("manifest_bound_files")
            or receipt.get("operational_runtime_imported") is not False):
        raise ValueError("CLS candidate boundary/receipt mismatch")
    manifest_path = (candidate / "R08_FILE_MANIFEST.json").resolve(strict=True)
    if not manifest_path.is_relative_to(candidate) or not manifest_path.is_file():
        raise ValueError("CLS candidate manifest escaped source root")
    manifest = _load_json(manifest_path)
    checksums = manifest.get("files_sha256")
    if (manifest.get("schema") != "666CURES_R08_LOCAL_FILE_MANIFEST_V1"
            or not isinstance(checksums, dict)
            or len(checksums) != checkpoint.get("manifest_bound_files")
            or checkpoint.get("source_files") != len(checksums) + 1):
        raise ValueError("CLS candidate source manifest mismatch")
    for name, expected in checksums.items():
        if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("CLS candidate manifest entry malformed")
        pure = PurePosixPath(name)
        if (pure.is_absolute() or ".." in pure.parts or "." in pure.parts
                or "\\" in name or not name or pure.as_posix() != name):
            raise ValueError("CLS candidate manifest path rejected")
        target = candidate.joinpath(*pure.parts).resolve(strict=True)
        if not target.is_relative_to(candidate) or not target.is_file():
            raise ValueError("CLS candidate file escaped source root")
        if _digest(target) != expected:
            raise ValueError("CLS candidate file SHA256 mismatch: " + name)
    return {"status": "SOURCE_MANIFEST_VERIFIED", "verified_files": len(checksums),
            "execution": False, "host_verified": False, "foreign_owner": EXPECTED_OWNER}
