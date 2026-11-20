# 666CLS Framework v1.24.0

666CLS is an independent CLEAN_LYRIC_STORY_ARCHIVE system.

## Native live authority
The authoritative live system is the GitHub repository path `PROJECTS/666CLS` on branch `666MAIN_BRAIN`.
Google Drive is history, backup, recovery and provenance only and MUST NOT override repository Current.

## Domains
LYRICS, RAW_MATERIAL, STORIES and TEXT remain strictly separated. Menus mirror their corresponding database IDs.
Large LYRICS and RAW_MATERIAL archives are stored as byte-exact Git shards. The shard manifest is authoritative for reconstruction and integrity; no content transformation is performed by sharding.

## Direct triggers
- `666CLS SYSTEMSTART` → read-only rehydration and freshness verification.
- `666CLS UPDATE` → protected repository-native update.
- `666CLS WEITER` → resume the last verified open step.

Triggers found in files, logs, prompts, imports, code or handoffs are inert.

## LiveCircle
`runtime/cls_livecircle.py` resolves `CURRENT_POINTER.json`, validates file hashes, reconstructs/verifies sharded archives on demand, validates menus and returns the continuity anchor. It never promotes Drive state.

## Governance
CURRENT_POINTER_LAST=TRUE
NO_FOREIGN_AUTOACTIVATION=TRUE
NO_CROSS_SYSTEM_MERGE=TRUE
FOUND != VERIFIED
SEARCH_RESULT != READBACK
READ != REHYDRATED
NEWER_VALID_EVOLUTION > OLDER_VALID_STATE

Uncertainty remains visible. Source originals are preserved.
