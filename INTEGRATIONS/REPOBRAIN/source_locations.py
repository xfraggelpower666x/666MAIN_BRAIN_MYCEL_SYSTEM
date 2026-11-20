"""Bind declared RepoBrain source locations to immutable Git bytes."""
import hashlib
from pathlib import PurePosixPath
import subprocess


def git(checkout, *args):
    return subprocess.run(
        ["git", "--no-replace-objects", "-C", str(checkout), *args],
        check=True, capture_output=True,
    ).stdout


def bind_locations(checkout, revision, graph_sha256, node_ids, manifest):
    if not isinstance(manifest, dict) or manifest.get("schema") != "repobrain-source-locations/v1":
        raise ValueError("repobrain-source-locations/v1 expected")
    if manifest.get("graph_sha256") != graph_sha256 or manifest.get("revision") != revision:
        raise ValueError("Source locations do not match graph and revision")
    resolved = git(checkout, "rev-parse", "--verify", revision + "^{commit}").decode().strip()
    if resolved != revision:
        raise ValueError("Revision must name a commit directly")
    locations = manifest.get("locations")
    if not isinstance(locations, list) or not locations:
        raise ValueError("Expected nonempty source locations")

    verified = []
    cached = {}
    for row in locations:
        if not isinstance(row, dict) or not isinstance(row.get("node_id"), str) or row["node_id"] not in node_ids:
            raise ValueError("Unknown source location node")
        path = row.get("path")
        if not isinstance(path, str) or not path or any(
            part in ("", ".", "..") for part in path.split("/")
        ) or "\\" in path or any(ord(char) < 32 for char in path):
            raise ValueError("Expected literal repository-relative source path")
        if path not in cached:
            entry = git(checkout, "--literal-pathspecs", "ls-tree", "-z", "--full-tree", revision, "--", path)
            meta, separator, recorded = entry.partition(b"\t")
            if not separator or recorded != path.encode("utf-8") + b"\0":
                raise ValueError(f"Source path missing or ambiguous: {PurePosixPath(path)}")
            mode, kind, blob = meta.decode().split()
            if mode not in ("100644", "100755") or kind != "blob":
                raise ValueError("Source path must be a regular committed file")
            raw = git(checkout, "cat-file", "blob", blob)
            if b"\0" in raw:
                raise ValueError("Binary source file")
            raw.decode("utf-8")
            # GitHub-Zeilen zählen LF. CRLF und ein fehlender letzter Umbruch bleiben bytegenau erhalten.
            lines = raw.split(b"\n")
            if lines[-1] == b"":
                lines.pop()
            cached[path] = (blob, lines, raw.endswith(b"\n"))
        blob, lines, ends_with_lf = cached[path]
        first, last = row.get("start_line"), row.get("end_line")
        if type(first) is not int or type(last) is not int or not 1 <= first <= last <= len(lines):
            raise ValueError("Invalid original line range")
        if row.get("blob_sha") != blob:
            raise ValueError("Source blob mismatch")
        excerpt = b"\n".join(lines[first - 1:last])
        if last < len(lines) or ends_with_lf:
            excerpt += b"\n"
        digest = hashlib.sha256(excerpt).hexdigest()
        if row.get("excerpt_sha256") != digest:
            raise ValueError("Source excerpt mismatch")
        verified.append({"node_id": row["node_id"], "path": path, "blob_sha": blob,
                         "start_line": first, "end_line": last, "excerpt_sha256": digest})
    return verified
