# CURRENTNESS + CONTRADICTION AUDIT

FACET=PSYLLO.SENTINEL
MODE=EVIDENCE_FIRST_READ_ONLY_UNLESS_UPDATE_AUTHORIZED

## Audit dimensions

- identity currentness
- repository authority
- branch / HEAD
- current pointer
- current state
- trigger contract
- LiveCircle / rehydration reachability
- facet reachability
- catalog-card freshness
- relation freshness
- open handoffs
- stale history risk
- authority collision
- cross-system merge risk
- lock / queue state
- pending readbacks
- visual contract parity

## Classification

VERIFIED
ABGELEITET
VORGESCHLAGEN
OFFEN
BLOCKIERT
PARTIAL
WRITE_BLOCKED
READBACK_PENDING
CONFLICT_QUARANTINE
STALE_REVALIDATION_REQUIRED

## Contradiction handling

NEW_EVIDENCE
→ COMPARE_WITH_CURRENT_RELATION
→ CLASSIFY_CONTRADICTION
→ CHECK_PROVENANCE
→ CHECK_RECENCY
→ CHECK_NATIVE_AUTHORITY
→ PRESERVE_BOTH_IF_UNRESOLVED
→ QUARANTINE_IF_AUTHORITY_COLLISION
→ PROMOTE_ONLY_VALID_SUPERSESSION

SILENT_OVERWRITE=FORBIDDEN
