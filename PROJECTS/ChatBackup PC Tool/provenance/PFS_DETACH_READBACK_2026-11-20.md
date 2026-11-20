# ChatBackup / PFS Detachment Readback — 2026-11-20

STATUS=PARTIAL
TARGET_REPOSITORY=xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
TARGET_BRANCH=migration/chatbackup-r1-detach-20261120
TARGET_ROOT=PROJECTS/ChatBackup PC Tool
SOURCE_REPOSITORY=xfraggelpower666x/666PFS_CSM
SOURCE_BRANCH=main
SOURCE_CHILD=children/CHATBACKUP-8001

## Verified
- Existing PC source files are editable in Git; R1 URL validation, regression, and Windows host probe were Git-blob checked.
- iPhone companion v1.0.9 is materialized at `mobile_scriptable/source`; JavaScript blob 706c63617506e9acccb92d6df5c76505d01f054a matches delivered R1.
- PFS history: 9/9 objects chosen for mirror have identical source and destination Git blob SHAs after commit and branch readback.
- Source PFS child retains 10 files; **9/10 total mirrored**.

## BLOCKER
FILE=backup/2026-10-28_VERIFIED_ORIGINALS/666_CHATBACKUP_PC_TOOL_v1.10.0.zip
SOURCE_SIZE_BYTES=13409046
SOURCE_GIT_BLOB=75547ff2dcd365b30a434d546803ae773ce07bc6
SOURCE_BLOB_READ=METADATA_ONLY
TRANSFER_API_RESULT=ZERO_LENGTH_CONTENT
DESTINATION_COPY=NOT_COMMITTED
PFS_CHILD_DELETE=FORBIDDEN_UNTIL_VERIFIED

## Other gates
- R1/bootstrap/bootstrap.ps1 expected Git blob 70844f51d42dc63ee3b2112634c604980ad32ac8: target still differs.
- iPhone R1 MANIFEST.sha256 expected blob 25562cf4cdc3e38908c13ba315838a15d30576b5: extracted original currently differs.
- R1 documents and validation receipts not yet fully repo-published.
- Windows EXE, true Windows GUI and Scriptable-iPhone device readback remain pending.
- PFS registry / inventory / dashboard / continuity / pointer not modified; production branch not merged.

## Next controlled action
1. Obtain intact 13,409,046-byte PFS original via authorized Git/Git LFS clone or other binary-capable transport, calculate Git blob SHA, and mirror as history.
2. Finish R1 file parity / regression on repository content and add detached project current declaration.
3. Verify source/target archive, then perform scoped PFS detach with backup, separate registry commit, readback, pointer last.
4. Merge Draft PR only after review and gates.

Do not claim full migration, production freeze or deletion until actual remote readback verifies each condition.
