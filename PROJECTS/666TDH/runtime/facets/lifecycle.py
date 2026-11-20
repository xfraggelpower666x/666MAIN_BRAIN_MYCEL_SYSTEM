"""666TDH child subfacets: one root authority, scoped read-only session continuity."""

from __future__ import annotations

from hashlib import sha256
import json


class FacetError(ValueError):
    """A binding or local continuity claim is not valid for current."""


def validate_bindings(data: dict, registry: dict, system_id: str) -> None:
    """Do not infer a branch, identity or source authority from old materials."""
    if data.get("system_id") != system_id or data.get("authority") != "REPOSITORY_PROJECT":
        raise FacetError("HOLD: Subfacetten-Autorität stimmt nicht")
    children = registry.get("children", {})
    profiles = data.get("child_profiles", {})
    if set(children) != set(profiles) or len(children) != 5:
        raise FacetError("HOLD: Subfacetten und Registry stimmen nicht überein")
    for token, child in children.items():
        profile = profiles[token]
        for field, want in (("branch_token", token), ("system_id", child["system_id"]),
                            ("version", child["version"]), ("current_path", child["current_path"])):
            if profile.get(field) != want:
                raise FacetError(f"HOLD: {token} {field} widerspricht Registry")
        adapter = f"runtime/hub/visual_adapters/{token}_VISUAL_ADAPTER.md"
        if profile.get("visual_adapter_path") != adapter:
            raise FacetError(f"HOLD: {token} Visual-Adapter nicht gebunden")
        if not isinstance(profile.get("local_lifecycle"), list) or not profile["local_lifecycle"]:
            raise FacetError(f"HOLD: {token} Sub-LiveCircle fehlt")
        if not isinstance(profile.get("ui_sections"), list) or not profile["ui_sections"]:
            raise FacetError(f"HOLD: {token} eigenes UI-Menü fehlt")
        if profile.get("child_update_authority") != "NONE":
            raise FacetError(f"HOLD: {token} hat unerlaubte Schreibautorität")


def scoped_continuity(checkpoint: dict | None, *, pointer_sha256: str, release: str,
                      target_system_id: str, branch_token: str | None,
                      provider_handoff: dict) -> dict:
    """A local, user-supplied checkpoint is evidence, never a new runtime pointer."""
    default = {"status": "NO_BOUND_HANDOFF", "open_step": None}
    if checkpoint is None:
        if provider_handoff.get("target_branch") != branch_token:
            return default
        return {"status": provider_handoff["status"], "open_step": provider_handoff["open_step"],
                "handoff_id": provider_handoff["handoff_id"]}
    if not isinstance(checkpoint, dict):
        raise FacetError("CONFLICT_QUARANTINE: ungültiges Checkpoint-Format")
    required = {"system_id": target_system_id, "branch_token": branch_token,
                "release": release, "pointer_sha256": pointer_sha256}
    if any(checkpoint.get(name) != value for name, value in required.items()):
        raise FacetError("CONFLICT_QUARANTINE: fremder, veralteter oder falscher Branch-Checkpoint")
    if checkpoint.get("runtime_authority", "NONE") != "NONE":
        raise FacetError("CONFLICT_QUARANTINE: Checkpoint darf keine Laufzeitautorität erhalten")
    fields = ("open_step", "development_position", "view_id")
    if any(key in checkpoint and checkpoint[key] is not None and
           (not isinstance(checkpoint[key], str) or len(checkpoint[key]) > 160)
           for key in fields):
        raise FacetError("HOLD: Checkpoint-Felder nicht zulässig")
    return {"status": "LOCAL_SCOPED_CHECKPOINT_UNVERIFIED_TASK", "open_step": checkpoint.get("open_step"),
            "development_position": checkpoint.get("development_position"),
            "view_id": checkpoint.get("view_id"), "runtime_authority": "NONE"}


def checkpoint_template(*, pointer_raw: bytes, release: str,
                        target_system_id: str, branch_token: str | None) -> dict:
    """Return a copyable structure; no automatic write and no authority."""
    return {"system_id": target_system_id, "branch_token": branch_token,
            "release": release, "pointer_sha256": sha256(pointer_raw).hexdigest(),
            "runtime_authority": "NONE", "open_step": None,
            "development_position": None, "view_id": None}


def profile_state(token: str, profile: dict) -> dict:
    """Only the directly selected child receives its subcircle state."""
    return {"branch_token": token, "system_id": profile["system_id"],
            "current_path": profile["current_path"], "sub_livecircle": list(profile["local_lifecycle"]),
            "rehydration": "ROOT_VERIFIED_THEN_SELECTED_CHILD_CURRENT_AND_PROFILE",
            "visual_adapter": profile["visual_adapter_path"],
            "holds": list(profile.get("holds", [])), "source_identity": profile.get("source_identity", "VERIFIED_OR_NOT_APPLICABLE"),
            "mutation_authority": "666TDH UPDATE"}
