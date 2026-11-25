# R07 development and audit

R07 adds independently anchored Ed25519 signature verification of a **canonical JSON registry snapshot**; bundled revision DAGs with fork, cycle, orphan and status-conflict checks; signed revocation list; and caller-supplied external monotonic sequence floor.

**Security boundary:** Caller-supplied trust-anchors must be independently obtained, verified, pinned and protected. Signature validity does not prove real-world issuer identity, provenance truth, or causal truth. Without external freshness floor, a valid older signed snapshot may be replayed. Without authenticated owner-key enrollment, attacker-controlled signed snapshots could pass. Signature cannot establish timestamp authenticity by itself. Revocation does not currently support independently validated historic reactivation or CRLs/OCSP.

R01-R06 entrypoints are additive and unchanged; R07 is a new pure function `candidate.signed_provenance_r07.verify_signed_sources` requiring `cryptography>=46,<47` (tested locally with 46.0.4). Tests use ephemeral Ed25519 test keys, **not production trust anchors**.

CLS reference interface is inert proposal. PFS native authorization is separate. No repo writes, no CLIC activity, no auto-load. Full historic engine remains missing.
