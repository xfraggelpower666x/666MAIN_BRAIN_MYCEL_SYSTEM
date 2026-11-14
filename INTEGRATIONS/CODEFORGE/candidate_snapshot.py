"""Derive a PyGate 0.3.2 snapshot for regular Git blobs."""
import hashlib
import json

from .check_patch_scope import git, scope_entry


def candidate_snapshot(checkout, candidate, checked_paths):
    """Hash the exact files declared by the receipt, using committed bytes."""
    if not isinstance(checked_paths, list) or not checked_paths:
        raise ValueError("Snapshot requires a nonempty list of checked paths")
    if not all(isinstance(path, str) and "\0" not in path for path in checked_paths):
        raise ValueError("Checked paths must be Git path strings")
    if len(set(checked_paths)) != len(checked_paths):
        raise ValueError("Duplicate checked path")

    records = []
    for path in sorted(checked_paths):
        scope_entry(path)
        raw = git(checkout, "--literal-pathspecs", "ls-tree", "-z", "--full-tree",
                  candidate, "--", path)
        header, sep, found = raw.removesuffix(b"\0").partition(b"\t")
        if not sep or found != path.encode("utf-8"):
            raise ValueError(f"Checked path is absent from candidate: {path!r}")
        mode, kind, blob = header.split()
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise ValueError(f"Checked path is not a regular Git blob: {path!r}")
        data = git(checkout, "cat-file", "blob", blob.decode("ascii"))
        records.append({"path": path, "exists": True, "size": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
