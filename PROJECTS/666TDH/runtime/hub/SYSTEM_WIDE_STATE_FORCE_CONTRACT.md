# 666TDH SYSTEM-WIDE STATE / FORCE / VISUAL CONTRACT v1.0

SCOPE=HUB|TD|LCTS|DAEMON|HANDOFF
SHARED_INFRASTRUCTURE=TRUE
SHARED_AUTHORITY=FALSE
NO_CROSS_SYSTEM_MERGE=TRUE

## Three-state storage law

LIVE_STATE=RUNTIME_CURRENT_AUTHORITY
HISTORY_STATE=HISTORICAL_EVIDENCE
BACKUP_STATE=RECOVERY_EVIDENCE

Each native area has its own subfolder in all three state roots:
HUB / TD / LCTS / DAEMON / HANDOFF.

LIVE_STATE must contain only one definitive current state per component.
Version pile-up in LIVE_STATE is forbidden.
Stable provider IDs and stable live filenames are preferred.
Before any live replacement:
PREWRITE_READ -> TARGET_LOCK -> BACKUP -> HISTORY_CHECKPOINT -> LIVE_REPLACE -> READBACK.

HISTORY_STATE is immutable evidence and may never become current merely because it is newer by timestamp.
BACKUP_STATE is recovery-only and may never become runtime authority without explicit recovery activation.

## FORCE inheritance

SYSTEMSTART=FORCE_2
WEITER=FORCE_2
NEW_CHAT=FORCE_4
AUTOMATIC_HANDOFF=FORCE_4
UPDATE=FORCE_5
HOST_RECOVERY=FORCE_5

Every component inherits the force quality of the invoking Hub operation.
This does not create child update authority.

## Visual inheritance

OPEN_RIGHT_FRAME=TRUE
FIXED_RULE_LENGTH=TRUE
SOFT_WRAP_MARGIN=3..5_CHARACTERS
RIGHT_FRAME_SYMBOL=NEVER
CONTINUATION_PREFIX=║
CONTINUATION_ALIGNMENT=MATCH_SEMANTIC_COLUMN
VISUAL_WIDTH_DRIFT=FORBIDDEN

20-segment status bars are evidence-gated.
100% is forbidden without verified evidence.
Subsystem labels must be native to the subsystem; foreign labels are never copied as authority.


## Daemon global FORCE hardening

DAEMON_FORCE_GLOBAL=TRUE
DAEMON_FORCE_INHERIT=OPERATION_LEVEL
DAEMON_REHYDRATE_GUARD=TRUE
DAEMON_WRITE_GUARD=TRUE
DAEMON_HANDOFF_GUARD=TRUE
DAEMON_RECOVERY_GUARD=TRUE
DAEMON_POINTER_GUARD=TRUE
DAEMON_VISIBLE_STATUS=TRUE
DAEMON_AUTHORITY=NONE
