"""Read-only verification of a repository-internal CODING PROFI live backup.

The native publisher owns creation of commits and optimistic HEAD leases.
This module NEVER changes a repository, plugin, local file or remote resource.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import re

PRIMARY = 'PROJECTS/LYVRA_CODING_PROFI'
BACKUP = 'PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE'
HEX40 = re.compile(r'^[0-9a-f]{40}$')

@dataclass(frozen=True)
class TreeReceipt:
    status: str
    source_path: str
    backup_path: str
    source_tree_sha: str | None
    backup_tree_sha: str | None
    source_commit: str | None
    backup_commit: str | None
    checked: bool
    primary_authority: str = 'plugins_6af753996b5c81918daadc40df266ce7'
    no_authority_transfer: bool = True


def verify_tree_pair(source_tree_sha: str | None, backup_tree_sha: str | None,
                     *, source_commit: str | None = None,
                     backup_commit: str | None = None) -> TreeReceipt:
    """A Git tree SHA is content-addressed: identical trees mean identical
    filenames, modes, blob bytes and nested directory structures.

    The provided SHAs MUST themselves come from an authenticated GitHub readback;
    caller-supplied claims alone do not establish trusted provenance.
    """
    valid = all(isinstance(s, str) and HEX40.fullmatch(s) for s in
                (source_tree_sha, backup_tree_sha, source_commit, backup_commit))
    if not valid:
        status = 'READBACK_PENDING'
    elif source_commit != backup_commit:
        status = 'BACKUP_STALE_REVISION'
    elif source_tree_sha != backup_tree_sha:
        status = 'BACKUP_TREE_MISMATCH'
    else:
        status = 'BACKUP_SYNC_VERIFIED'
    return TreeReceipt(status, PRIMARY, BACKUP, source_tree_sha,
                       backup_tree_sha, source_commit, backup_commit,
                       status == 'BACKUP_SYNC_VERIFIED')


def review_host_receipt(value: Mapping[str, Any] | None) -> str:
    """Never treat backup verification as independent plugin host acceptance."""
    if not isinstance(value, Mapping):
        return 'HOST_READBACK_PENDING'
    if value.get('claimed_host_verified') is True:
        return 'HOST_CLAIM_NOT_ADOPTED'
    return 'HOST_NOT_TESTED'
