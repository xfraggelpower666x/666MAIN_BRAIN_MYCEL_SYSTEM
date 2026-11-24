# 666 CODEFORGE ALLIANCE — LIVE BACKUP CONTRACT R02

**Owner of backup:** 666 CODEFORGE ALLIANCE development mirror under `666MAIN_BRAIN/PROJECTS/666_CODEFORGE_ALLIANCE/`.
**Role:** ADDITIVE_LIVE_BACKUP; never native authority, not an execution host, not a replacement for a primary project, plugin or source repository.
**State:** POLICY_PUBLISHED; AUTOMATIC_SYNC_NOT_INSTALLED.

## Source of truth and scope
- Each native project and plugin retains its own identity, code, Current Pointer, authoritative branch, runtime, plugin release and update governance.
- This GitHub folder is an auxiliary, versioned backup and engineering handoff surface. It must not relocate, take over or supersede any native project.
- Backup source selection is explicit per change. An external/peer system is not copied merely because it participates in a CodeForge capability review.
- Only approved, scoped content may be mirrored. Secrets, tokens, private archives, personal chat exports and unapproved foreign source code are forbidden.

## Required live-backup transaction on every authorized source change
1. Resolve the exact primary native authority and its fresh verified revision/release ID.
2. Identify the changed content and the owning project's authorized export/sync interface.
3. Preserve the prior backup commit and create/identify a recovery point; do not erase older backups.
4. Compare fingerprints and content. Publish changed approved artifacts only, preserving every unrelated file and sibling PROJECTS directory.
5. Pin source revision, release, paths, timestamp, checksum and scoped evidence in a new backup receipt. Never use a source-only snapshot as evidence of host acceptance.
6. Gate repository updates by the fresh expected branch HEAD; halt with CONFLICT_QUARANTINE if the branch moves unexpectedly.
7. Read back every changed file at the published commit and check hashes against the source-approved payload.
8. Only after successful readback may that particular source revision be marked BACKUP_SYNC_VERIFIED.
9. If backup publication fails, preserve the primary update and mark BACKUP_SYNC_PENDING with an exact retry/recovery anchor; never roll back the native system merely to match this secondary copy.
10. Native systems remain responsible for their own updates. A CodeForge Alliance coordinator may review and request a scoped handoff but cannot acquire native execution authority.

## Trigger and enforcement boundary
- The desired trigger is **every successful native source change** that explicitly includes this backup target in its source-owned update contract.
- GitHub commits in this backup repository alone cannot detect changes to other repositories or private plugin releases.
- A dedicated source-owned trigger, authorized workflow, or approved update-step integration is required per primary source. **No such universal cross-repository or plugin-host trigger is currently installed by this R02 policy.**
- Never claim automatic synchronization until an event is observed end-to-end with source revision, delivery, backup commit and independent readback.

## Independence invariant
`PRIMARY_LOCATION_UNCHANGED=TRUE`
`PRIMARY_PURPOSE_UNCHANGED=TRUE`
`NATIVE_AUTHORITY_UNCHANGED=TRUE`
`NO_CROSS_SYSTEM_MERGE=TRUE`
`NO_FOREIGN_AUTOACTIVATION=TRUE`
`NO_SILENT_OVERWRITE=TRUE`
`BACKUP_NE_RUNTIME=TRUE`
`BACKUP_NE_PRIMARY=TRUE`

## Existing R01 preservation
The initial 10-file R01 snapshot remains preserved (commit `a853c69a4751742faf052c6f7b5b924d73e66f2c`).
The R01 `SOURCE_MANIFEST.json` is the R01 artifact inventory and is not silently rewritten into a false cross-repository live-sync receipt.
The R01 ACE code and tests are development candidates, not active plugin runtimes.

## Next actual engineering gate
Select and verify each primary project's specific change notification/export contract. Implement a least-privilege source-owned sync hook, use a synthetic change, then require end-to-end SHA/release/backup readback before setting `AUTO_SYNC_VERIFIED`.
