# Scriptable iPhone Companion Integration — PC Tool v1.10.3

Current companion: `666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.7.zip`.

This release does not change Scriptable runtime code. It hardens package governance around the already-current v1.0.7 companion:

- byte/hash verification;
- embedded `VERSION.json` verification;
- embedded `MANIFEST.sha256` verification;
- explicit Current-vs-History path checks;
- `CURRENT_RELEASE_INDEX.md` anchor.

Older v1.0.6 and v1.0.0 packages remain under `mobile_scriptable/history/` as provenance only.
