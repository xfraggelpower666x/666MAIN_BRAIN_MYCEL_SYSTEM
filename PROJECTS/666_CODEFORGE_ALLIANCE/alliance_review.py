"""Review-only Alliance handoff helper. Not a controller, dispatcher or authority."""
from __future__ import annotations

REQUIRED = frozenset(("handoff_id", "source_system_id", "target_system_id",
    "native_current_ref", "source_revision", "capability_id", "task_id",
    "read_scope", "write_scope", "dependencies", "delivery_receipt",
    "acceptance_receipt", "evidence_refs", "status"))

class AllianceRejected(ValueError):
    pass


def inspect_handoff(offer: dict) -> dict:
    """Inspect untrusted offers; never attest native current or permission."""
    if not isinstance(offer, dict) or set(offer) != REQUIRED:
        raise AllianceRejected("INVALID_HANDOFF_SHAPE")
    for field in REQUIRED - {"dependencies", "evidence_refs", "read_scope", "write_scope"}:
        if not isinstance(offer[field], str) or not offer[field].strip():
            raise AllianceRejected("INVALID_" + field.upper())
    if any(not isinstance(offer[f], list) or any(not isinstance(v, str) or not v for v in offer[f])
           for f in ("dependencies", "evidence_refs", "read_scope", "write_scope")):
        raise AllianceRejected("INVALID_HANDOFF_LIST")
    if offer["source_system_id"] == offer["target_system_id"]:
        raise AllianceRejected("SELF_PEER_HANDOFF")
    return {"handoff_id": offer["handoff_id"], "task_id": offer["task_id"],
            "source_system_id": offer["source_system_id"],
            "target_system_id": offer["target_system_id"],
            "result": "REVIEW_ONLY", "native_current_verified": False,
            "source_permission_verified": False, "recipient_ack_verified": False,
            "host_dispatch_performed": False, "writes_performed": False,
            "next_gate": "INDEPENDENT_NATIVE_CURRENT_PERMISSION_AND_HOST_RECEIPT"}
