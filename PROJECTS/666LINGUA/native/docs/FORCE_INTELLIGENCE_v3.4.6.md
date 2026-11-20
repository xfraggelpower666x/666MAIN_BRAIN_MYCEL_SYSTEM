# 666LINGUA FORCE Intelligence v3.4.6

## 666LINGUA FORCE Intelligence Contract v3.4.6

FORCE_INTELLIGENCE=ACTIVE_MANDATORY
FORCE_INTELLIGENCE_DISABLE=FORBIDDEN
FORCE_INTELLIGENCE_SCOPE=READ|REHYDRATE|WRITE|READBACK|HANDOFF|NEW_CHAT|RESTORE|POINTER

IMPORTANT:
666LINGUA FORCE ON/OFF/STATUS remains the user-facing Translation Engine
Force Lock. Core FORCE Intelligence is a separate always-on governance layer.
"666LINGUA FORCE OFF" MUST NOT disable Core FORCE Intelligence.

FORCE_READ_GATE:
1. Resolve exact system identity.
2. Resolve Current Pointer by canonical ID.
3. Verify version, provenance, supersession, freshness and authority class.
4. Reject HISTORY/BACKUP as boot authority when valid LIVE_CURRENT exists.
5. Read the referenced LIVE_CURRENT files.
6. Require direct provider readback where a write or critical recovery is involved.
7. FOUND != VERIFIED; READ != REHYDRATED.

FORCE_REHYDRATE_GATE:
1. Consume Current Pointer completely.
2. Consume CURRENT_STATE_POINTER from LIVE_CURRENT.
3. Load only state files explicitly referenced by the live state pointer.
4. Compare system_id, version/schema, authority, freshness and supersession.
5. Fail closed on contradictory live authorities.
6. Do not silently fall back to History or Backup.
7. Use Backup only through explicit RESTORE/recovery logic.
8. Mark REHYDRATED only after all required live state is coherent.

FORCE_WRITE_GATE:
1. Verify connector.
2. Verify rights.
3. Verify exact target.
4. Verify authority class.
5. Verify scope and intended version.
6. Create PRECHANGE backup before relevant mutation.
7. Write LIVE_CURRENT in-place preserving stable file IDs.
8. Directly read back the provider result.
9. Validate content, identity, version and authority.
10. Only after readback PASS create History checkpoint.
11. Update Current Pointer LAST.
12. No native mutation after pointer in the same publication cycle.

FORCE_READBACK_GATE:
WRITE_RESULT_NE_VERIFIED=TRUE
DIRECT_PROVIDER_READBACK=MANDATORY
EXPECTED_VS_ACTUAL_COMPARE=MANDATORY
MISMATCH_ACTION=STOP_REPAIR_NO_POINTER_ADVANCE

FORCE_HANDOFF_GATE:
HANDOFF_SOURCE=VERIFIED_LIVE_CURRENT_ONLY
OPEN_TASK_STATE_REQUIRED=TRUE
LAST_VERIFIED_CHECKPOINT_REQUIRED=TRUE
HISTORY_AS_HANDOFF_SOURCE=FORBIDDEN_BY_DEFAULT
BACKUP_AS_HANDOFF_SOURCE=FORBIDDEN_BY_DEFAULT
AUTOMATIC_HANDOFF_MUST_CAPTURE_CURRENT_AUTHORITY_REFERENCES=TRUE
HANDOFF_NE_BOOT_AUTHORITY=TRUE

FORCE_NEW_CHAT_GATE:
NEW_CHAT_SOURCE=CURRENT_POINTER_PLUS_LIVE_CURRENT
NEW_CHAT_MUST_REHYDRATE_BEFORE_NEW_SETUP=TRUE
NEW_CHAT_MUST_NOT_GUESS_LATEST_STATE=TRUE
NEW_CHAT_MUST_NOT_SELECT_NEWEST_FILENAME_BY_NAME_ONLY=TRUE
NEW_CHAT_HISTORY_FALLBACK=FORBIDDEN_IF_LIVE_VALID
NEW_CHAT_BACKUP_FALLBACK=RESTORE_ONLY

FORCE_POINTER_GATE:
POINTER_WRITE=LAST_NATIVE_MUTATION
POINTER_ADVANCE_REQUIRES_ALL_REQUIRED_READBACK_PASS=TRUE
POINTER_TO_UNVERIFIED_STATE=FORBIDDEN

FORCE_RESTORE_GATE:
RESTORE_TRIGGER_REQUIRED=TRUE
RESTORE_SOURCE_MUST_BE_VERIFIED_BACKUP_OR_HISTORY_CHECKPOINT=TRUE
RESTORE_MUST_CREATE_PRE_RESTORE_BACKUP=TRUE
RESTORE_MUST_READBACK_BEFORE_POINTER_ADVANCE=TRUE
