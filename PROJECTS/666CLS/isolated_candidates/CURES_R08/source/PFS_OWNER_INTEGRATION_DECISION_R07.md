# 666CURES R07 · PFS owner decision package (read-only)

Canonical repo: `xfraggelpower666x/666PFS_CSM`, branch `main`.
Read HEAD `08989d5dc71259cbebf108c71d2e315aa9ac28a1` at audit time.
`SYSTEM_IDENTITY.md` blob `3f6c38fbff54709e511bace3a0962c03853d53cb`.
`REHYDRATION.md` blob `ff5c4364a6fdb59966c3e7865bf3893b302a38c0`.
`SOURCE_BINDING.md` blob `f40e54c1916960365513f2fcddc27ee774880c3b`.

**HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND** and `CHILD_AUTOLOAD=FORBIDDEN` remain binding.

R07 is new candidate code, **not recovered historical CURES executable bytes**. Its Ed25519 test key is generated only in volatile tests. No real issuer-verified certificate, pinned real-world owner key, signed live source registry, transparency log, trusted external freshness watermark or native owner acceptance is supplied.

Before any PFS integration: separate PFS owner authorization; independently attest signer identity and pin public key; define key rotation/revocation and anti-rollback storage; backup protected target; check branch/commit conflict lock; import only approved candidate under new provenance, not as recovered original; run targeted regression and CI; verify exact commit/tree/blob readback; pointer last with no subsequent writes. None of these publishing gates has been executed.
