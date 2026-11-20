# Scriptable iPhone Companion Integration — PC Tool v1.10.1

## Current companion

`666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.6.zip`

## Integration repair

PC v1.10.0 still bundled the original v1.0.0 mobile companion even though the mobile parser had evolved through v1.0.5. v1.10.1 repairs that package drift without changing the PC chat parser architecture.

The current mobile companion adds:

- variant-tolerant React-Flight + SSR share handling;
- direct raw-HTML SSR transcript parsing before WebView fallback;
- source-format fingerprint diagnostics;
- fail-closed identity handling;
- existing manual/group/image/export/language capabilities preserved.

The original v1.0.0 mobile ZIP remains under `mobile_scriptable/history/` for provenance.
