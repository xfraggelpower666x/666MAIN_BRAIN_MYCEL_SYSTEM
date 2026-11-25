# 666CURES isolated candidate R07

Non-production additive candidate based on R06. **Not historical CURES engine**.

## R07 capabilities
- `candidate.signed_provenance_r07.verify_signed_sources(documents, signed_envelope, trust_anchors, minimum_sequence=None)`
- Ed25519 verification; independently provided pinned 32-byte raw public key by `key_id`; canonical JSON; signed registry, source revision graph and revocation list
- Validates revision parent edges and rejects cycles, cross-document lineages, orphans and duplicate IDs; preserves forks and temporal conflicts
- Optional caller-supplied persistent monotonic sequence floor; no anti-rollback claim if omitted
- No network, file I/O, auto-load, state mutation, hidden trust promotion or foreign system writes

Run: `python -m unittest discover -s tests -p 'test_candidate_r*.py' -v`
Plus R01: `python -m unittest discover -s R01_CONTRACT/tests -p 'test_*.py' -v`
And R01 smoke: `python R01_CONTRACT/tools/check_candidate.py candidate/cures_candidate.py` (depending on tool CLI).

Dependency: `python -m pip install -r requirements-r07.txt` in isolated environment.

**Boundary:** Trust anchor enrollment and identity must be verified externally. Signature validity is not factual correctness; timestamp and revocation freshness require independent evidence. No CLS/PFS current change.
