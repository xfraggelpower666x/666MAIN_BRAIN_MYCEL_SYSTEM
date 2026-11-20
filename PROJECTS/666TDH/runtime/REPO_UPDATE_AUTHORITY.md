# 666TDH Repository-Native Protected Update Authority - R1 (2026-11-20)

SYSTEM_ID=666TRACKHUB-001
NAMESPACE=666TDH
CANONICAL_TRIGGER=666TDH UPDATE
AUTHORITY=REPOSITORY_PROJECT
PRODUCTIVE_REPOSITORY=xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
PRODUCTIVE_BRANCH=666MAIN_BRAIN
ALLOWED_WRITE_ROOT=PROJECTS/666TDH
SOURCE_NATIVE_RELEASE=v1.15.0
REPO_POLICY_REVISION=R1
CURRENT_POINTER_LAST=TRUE
POST_POINTER_MUTATION=FORBIDDEN
PFS_RUNTIME_AUTHORITY=NONE
PFS_DEPLOY_AUTHORITY=NONE
PFS_AUTOLOAD=FORBIDDEN
PFS_MUTATION_FROM_TDH=FORBIDDEN
FOREIGN_SYSTEM_AUTOACTIVATION=FORBIDDEN
NO_CROSS_SYSTEM_MERGE=TRUE

## Canonical precedence
1. Repository HEAD -> PROJECTS/666TDH/CURRENT_POINTER.json -> verified file hashes.
2. runtime/REGISTRY.json, runtime/TRIGGERS.json, runtime/REHYDRATION.md, runtime/LIVECIRCLE.md and THIS FILE.
3. Child Current only for a directly selected registered branch.
4. Source provider files under runtime/hub and provenance are retained evidence, not competing repo authority.

The provider-era update instructions in runtime/hub/UPDATE_LIFECYCLE.md,
runtime/hub/UNIVERSAL_UPDATE_SAVE.md and runtime/hub/LIVE_SYNC_POLICY.md
describe the historical Live Drive plus PFS dual-publish lifecycle.
They remain intact for provenance. Their requirements to write Drive, PFS
releases, PFS core pointers or PFS backups DO NOT govern repo-native updates.
PFS TRACKHUB-32001 is external recovery only. Its own authority is required
for any PFS mutation. The shared MAIN BRAIN repository is a host, not an
execution-authority override.

## Protected repo transaction
1. Resolve the productive branch HEAD and current pointer at one commit; verify
   identity, declared scope, registry, freshness, handoff, expected files and hashes.
2. Validate repository write permission, expected head, branch protection/lock
   and the complete intended change set. Fail closed on missing evidence.
3. Create a restorable pre-change Git ref from the exact outgoing commit. Keep
   the outgoing commit as immutable history. Preserve original source vault.
4. Audit the real delta; apply only TDH-native minimal changes to the working
   tree. Never relabel unchanged child source/data versions.
5. Run the applicable regression, integrity, isolation and negative tests.
   Do not invent host-render, external recovery or PFS readback passes.
6. Freeze the audited repo file set; prepare a data commit. Read the staged
   contents and re-audit against expected hashes and path boundaries.
7. Prepare a final commit that changes CURRENT_POINTER.json only, as the
   last commit in the update chain. All pointed-to hashes must match.
8. Move the productive ref by a checked fast-forward / optimistic lease
   from the verified outgoing HEAD to that final commit.
9. Read back productive HEAD, pointer, affected data files and hash bindings.
   After final pointer publication perform NO FURTHER MUTATION in this update.
10. If a gate fails, report WRITE_BLOCKED or READBACK_PENDING with exact
    evidence. Never promote a partially published release.

## Current boundaries
Child identities and releases: TD, LCTS, DTSTE, FSE, SHACHIVITI remain
separate; no child UPDATE trigger, no cross-child content inheritance.
FSE source-original archive: SOURCE_VAULT_ONLY due to potential credentials;
never copy it into this public repository or reveal its contents.
FSE and SHACHIVITI original native identities: UNRESOLVED_HOLD.
History, backups and provider recovery: cold references, never autoload.
Interactive GPT-native host rendering: OPEN_NOT_VERIFIED until real acceptance.
Current Handoff: continuity only, RUNTIME_AUTHORITY=NONE.
