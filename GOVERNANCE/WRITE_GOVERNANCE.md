# WRITE GOVERNANCE

## Protected write sequence

1. Resolve exact target and authority.
2. Verify repository, branch and permissions.
3. Verify current pointer revision / HEAD.
4. Create pre-change recovery evidence.
5. Apply minimal body changes.
6. Read back each changed body.
7. Run contradiction and antidrift checks.
8. Publish the applicable current pointer last.
9. Perform pointer readback.
10. No further mutation in the same update.

## Migration authority gate

During incomplete migration:

REPOSITORY_ROLE=ACTIVE_BUILD_AND_VERIFICATION_SURFACE
DRIVE_ROLE=MIGRATION_SOURCE_RECOVERY
DRIVE_HISTORY_ONLY=FALSE

Only after FINAL_COMPLETION_GATE and final repository pointer readback:

REPO_FIRST_AUTH=TRUE
DRIVE_ROLE=HISTORY_ONLY
DRIVE_CURRENT_AUTHORITY=NONE

PREMATURE_DRIVE_HISTORY_ONLY=FORBIDDEN
PREMATURE_REPO_FIRST_AUTH_CLAIM=FORBIDDEN

## Public repository safety

PUBLIC_REPO=TRUE
SECRETS_IN_REPO=FORBIDDEN
TOKENS_IN_REPO=FORBIDDEN
PRIVATE_DRIVE_IDS_IN_REPO=FORBIDDEN
PRIVATE_CONVERSATION_CONTEXT_IN_REPO=FORBIDDEN

## Cross-system safety

FOREIGN_NATIVE_WRITE_REQUIRES_FOREIGN_NATIVE_AUTHORITY=TRUE
MAIN_BRAIN_MAY_CATALOG_FOREIGN_SYSTEM=TRUE
MAIN_BRAIN_MAY_NOT_MUTATE_FOREIGN_SYSTEM_BY_CATALOGING=TRUE
