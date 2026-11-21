#!/usr/bin/env python3
"""R06: pure, bounded MYCEL -> Coding Profi project-scope binding, never an executor."""
from __future__ import annotations

import re
from typing import Mapping

OWNER = "666MAIN BRAIN MYCEL SYSTEM"
FACET = "PSYLLO.DEV"
PROVIDER = "L.Y.V.R.A. CODING PROFI"
FIELDS = ("project_id", "source_repository", "source_branch", "source_head",
          "lineage_id", "owner", "return_anchor")
VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,179}$", re.ASCII)
SHA = re.compile(r"^[0-9a-f]{40}$", re.ASCII)


class BindingConflict(ValueError):
    """Checkpoint does not belong to the selected, verified project/revision/lineage."""


class BindingIncomplete(ValueError):
    """Project or authoritative source cannot yet be resolved; do not activate."""


def _identity(value: object, field: str) -> str:
    if not isinstance(value, str) or not VALUE.fullmatch(value):
        raise BindingIncomplete(field + ": missing or unsafe project identifier")
    return value


def bind_project(*, whole_verified: bool, facet_id: str,
                 current: Mapping[str, object] | None,
                 checkpoint: Mapping[str, object] | None = None) -> dict:
    """Produce a read-only method routing decision after native Current verification.

    No tools are invoked; no global/foreign Current, plugin activation or storage changes.
    """
    if whole_verified is not True:
        raise BindingIncomplete("MAIN BRAIN Whole Current was not verified")
    if facet_id != FACET:
        raise BindingConflict("Only the existing PSYLLO.DEV facet may use this method")
    if not isinstance(current, Mapping):
        raise BindingIncomplete("No verified coding project selected")

    selected = {key: _identity(current.get(key), key) for key in FIELDS if key != "owner"}
    if current.get("owner") != OWNER:
        raise BindingConflict("Project owner is not the authorised MAIN BRAIN owner")
    selected["owner"] = OWNER
    if not SHA.fullmatch(selected["source_head"]):
        raise BindingIncomplete("source_head: full lowercase Git SHA required")
    if not isinstance(checkpoint, Mapping) and checkpoint is not None:
        raise BindingConflict("Checkpoint must be a mapping")
    if checkpoint is not None:
        for field in ("project_id", "source_repository", "source_branch",
                      "source_head", "lineage_id", "owner"):
            if checkpoint.get(field) != selected[field]:
                raise BindingConflict("Stale or foreign checkpoint: " + field)
    return {
        "owner": OWNER,
        "facet_id": FACET,
        "method_provider": PROVIDER,
        "project": selected,
        "checkpoint_accepted": checkpoint is not None,
        "execution_authority": "NONE_METHOD_ROUTING_ONLY",
        "provider_lifecircle": "PROJECT_SCOPED_ONLY",
        "whole_ownership": "666MAIN BRAIN",
        "foreign_autoactivation": False,
        "source_status": "SOURCE_BOUND_HOST_UNVERIFIED",
        "next_step": "READ_INSTALLED_PROVIDER_SKILL_AND_VALIDATE_PROJECT_AUTHORITY",
    }
