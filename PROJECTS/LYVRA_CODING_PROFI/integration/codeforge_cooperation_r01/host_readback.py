"""Bounded read-only connector seam for CODING PROFI; no provider credentials or writes."""
from dataclasses import dataclass
from hashlib import sha1
from coordination import WorkOffer

MAX_SOURCE_BYTES = 1024 * 1024

@dataclass(frozen=True)
class BoundGitHubSource:
    native_owner: str
    repository: str
    branch: str

def _blob_sha(content: str) -> str:
    encoded = content.encode("utf-8")
    return sha1(b"blob " + str(len(encoded)).encode("ascii") + bytes((0,)) + encoded).hexdigest()

def read_via_connector(offer: WorkOffer, binding: BoundGitHubSource, read_head, read_file) -> dict:
    """Injected host readers; verify two HEAD reads, immutable file blob, and owner binding.

    read_head(repo, branch) -> 40-char HEAD string
    read_file(repo, path, commit) -> dict {"content":str, "sha":40-char blob SHA}
    Does not execute any plugin-native action. Caller must invoke approved host connector.
    """
    offer.validate()
    if offer.mode != "READ_ONLY":
        raise ValueError("only READ_ONLY offer may reach the connector")
    if offer.source.status != "SOURCE_VERIFIED" or not offer.source.readback:
        raise ValueError("unverified source")
    if (offer.native_owner, offer.source.repository, offer.source.branch) != (
        binding.native_owner, binding.repository, binding.branch
    ):
        raise ValueError("native binding mismatch")
    source = offer.source
    if read_head(binding.repository, binding.branch) != source.commit:
        raise ValueError("stale native branch")
    files = []
    for path in offer.target_paths:
        result = read_file(binding.repository, path, source.commit)
        if not isinstance(result, dict) or not isinstance(result.get("content"), str):
            raise ValueError("invalid host read result")
        content = result["content"]
        if len(content.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise ValueError("oversize host result")
        actual = _blob_sha(content)
        if result.get("sha") != actual:
            raise ValueError("blob hash mismatch")
        files.append({"path": path, "blob_sha": actual, "bytes": len(content.encode("utf-8"))})
    if read_head(binding.repository, binding.branch) != source.commit:
        raise ValueError("branch moved during read")
    return {
        "offer_id": offer.offer_id,
        "lead": "CODING_PROFI",
        "native_owner": binding.native_owner,
        "repository": binding.repository,
        "branch": binding.branch,
        "source_commit": source.commit,
        "result": "HOST_GITHUB_READBACK_ACCEPTED",
        "files": files,
        "plugin_native_execution": "NOT_PROVEN",
        "foreign_writes": False,
        "authority_transfer": False,
    }
