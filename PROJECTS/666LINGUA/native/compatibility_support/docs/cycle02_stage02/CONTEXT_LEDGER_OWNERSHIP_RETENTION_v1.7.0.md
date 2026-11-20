# Context Ledger Ownership and Retention v1.7.0

- Owner: current Dolmetscher session state; no independent memory root.
- Binding: existing INPUT_HOLD, checkpoint and recovery identifiers.
- Data classes: source text hash, target profile, relationship profile reference, correction lineage, output hash, expiry marker.
- Default retention: session-bound unless the user explicitly requests persistence.
- Persistent retention duration: `UNASSIGNED_BY_USER_POLICY`; therefore no invented fixed time value.
- Deletion: source record, derived correction lineage, cached output and test candidate references are traversed and removed together.
- Audit records retain only non-content evidence where possible.
