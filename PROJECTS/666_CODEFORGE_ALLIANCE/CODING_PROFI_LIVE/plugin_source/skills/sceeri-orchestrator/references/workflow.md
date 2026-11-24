# SCEERI decision contract v0.1.0

Sequence: SCOPE → SEMANTICS → EVIDENCE → CAUSALITY → RELATIONS → EMERGENT HYPOTHESES → REPAIR GATE → VERIFIED OUTCOME → HANDOFF.

Output each significant claim as: `claim_id`, `claim`, `status`, `sources`, `time`, `uncertainty`, `next_verification`.

A self-healing attempt must include: `precondition`, `authorization`, `backup`, `minimal_diff`, `tests`, `readback`, `rollback`, `pointer_last` and `post_publish_mutation=false`.

Supported statuses: VERIFIZIERT, ABGELEITET, VORGESCHLAGEN, OFFEN, BLOCKIERT, PARTIAL, WRITE_BLOCKED, READBACK_PENDING, CONFLICT_QUARANTINE.

This skill is instruction-only. It has no persistent state, no background scheduler, no connector authority and no automatic write permission.
