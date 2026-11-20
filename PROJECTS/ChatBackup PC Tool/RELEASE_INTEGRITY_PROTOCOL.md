# Release Integrity Protocol — v1.10.5

`VERIFY_RELEASE_INTEGRITY.bat` / `tests/release_integrity_probe.py` verify the Current package without pytest.

Current contract covers **16 checks**:

- paths and SHA-256 hashes of the released PC files in `MANIFEST.sha256`;
- current Scriptable v1.0.9 ZIP and SHA exist and match;
- embedded mobile `VERSION.json` is v1.0.9;
- embedded mobile manifest is complete and hash-valid;
- v1.0.9 contains the host-acceptance contract and receipt schema;
- Windows host-acceptance Python/BAT contract is present;
- `CURRENT_RELEASE_INDEX.md` identifies PC v1.10.5 and mobile v1.0.9;
- `SOURCE_MAPPING.md` points to current v1.0.9 and not historical v1.0.0 as Current;
- historical v1.0.0, v1.0.6, v1.0.7 and v1.0.8 packages remain history-scoped.

Only `RELEASE_INTEGRITY_PASS` is accepted. This verifies package governance; it does not substitute for a real Windows/iPhone host receipt.
