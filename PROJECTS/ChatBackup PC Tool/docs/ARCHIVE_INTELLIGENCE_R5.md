# ChatBackup Archive Intelligence R5 — optional offline module

STATUS=FEATURE_BRANCH_CANDIDATE
CORE_VERSION_UNCHANGED=1.10.5
SCRIPTABLE_VERSION_UNCHANGED=1.0.9
PFS_SCOPE=NONE

## Functions
- Official user-downloaded ChatGPT data-export ZIP reader: exactly one conversations.json, no unpack/extraction, no network or account credentials.
- Preserves each mapping node and parent relationship, including alternate assistant branches. Asset references do not claim downloadable bytes.
- ZIP validation: traversal, symlink, encrypted member, duplicate entry, decompression budget and size limits.
- Local searchable SQLite derived catalog with message-identity and SHA-256 revision dedup; original ZIP remains untouched.
- Completeness reports PARTIAL for unresolved media or unsupported content, never fake 100% recovery.
- Optional research JSONL with source ID, parent node, exact offsets and SHA-256 per chunk.
- Separate Python interface, no changes to existing .py/.pyw GUI, EXE, backend, scripts or iPhone release.

## Run
In the project root:
\`\`\`bash
python tools/archive_intelligence_cli.py inspect export.zip
python tools/archive_intelligence_cli.py import export.zip
python tools/archive_intelligence_cli.py search "example"
python tools/archive_intelligence_cli.py status
python tools/archive_intelligence_cli.py rag export.zip research.jsonl
\`\`\`
SQLite default: ~/.666chatbackup/catalog.sqlite3. Use --db PATH before the subcommand to override.

## Constraints and compatibility
The adapter only claims support for mapping-based conversations.json and does not reconstruct chat.html or index.html into fake records. Huge archives deliberately fail closed. The catalog is a rebuildable derivative; it is not a substitute for the source ZIP. No cookies, undocumented endpoints or third-party code have been copied. This is not yet bundled into the Windows EXE, and has not been tested on a user's actual PC or iPhone.

## Abnahme
New offline pytest fixtures, Python compilation, existing baseline and Release Integrity must be verified before production merge. No freeze based solely on synthetic tests.

## Nächste sinnvolle Recherchepunkte
1. More anonymized official export format fixtures and schema evolution.
2. Bounded streaming JSON and progress/cancel/resume.
3. Role/date filters and indexed FTS5 for very large archives.
4. Opt-in Tkinter archive window and integration with existing GUI without rewriting it.
5. Import previously saved standalone ChatBackup JSON and Scriptable folders as separate adapters.
