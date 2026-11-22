# R03 Architecture and Recovery

## Boundaries
- Renderer = visual-only UI. Electron preload exposes an allowlisted set of IPC methods; contextIsolation, sandbox and no nodeIntegration.
- Electron main = file-picker, tool probes, Python process invocation and OS folder open. It does not parse imported data for executable instructions.
- Python `engine/bridge.py` = SQLite transaction owner and trusted extraction boundary. Every request is a JSON packet through stdin/stdout, no TCP server.
- `catalog.sqlite` = canonical relational state. Index JSON = derived snapshot from table metadata. Per-record JSON = incremental materialization. Files are not re-analyzed for browsing.
- Legacy R02 = immutable packaged copy, migratable read-only.

## Data flow
Choose/drop files -> type-safe ZIP extraction -> structural segmentation -> source hash -> classify project/category/topics -> transactional SQLite insert -> new JSON record files -> project/global indexes -> dashboard/browser/export. Reimports are idempotent for same project/category/body.

## Migration
Legacy V2.2/R02 source remains independent. Explicit UI migration reads `legacy_r02/app/lyrics_library.db` with SQLite mode=ro, writes separate catalog rows, and materializes new JSON.

## Archive and recovery
User selects record -> ZIP with individual JSON and `index.json` -> CRC check -> move to `old_archive/` -> DB mark archived -> index refresh. Readback path and record identifiers are returned to the UI. No physical DB deletes.

## Recommended next checks
1. Windows GUI/Electron execution on real host.
2. Input security and performance with real ChatGPT export sizes (>100 MB should be split into smaller inputs under present guardrails).
3. Content-corpus classification precision and manual reconciliation of project identities.
4. Native project comparison only after authorized GitHub Current readback.
5. Optional independent indexing worker and project reassignment UI without cross-system merges.
