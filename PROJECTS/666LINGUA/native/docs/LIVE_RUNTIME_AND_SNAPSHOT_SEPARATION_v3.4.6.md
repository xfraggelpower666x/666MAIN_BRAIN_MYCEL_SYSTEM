# 666LINGUA Live Runtime & Snapshot Separation v3.4.6

## 666LINGUA Live Runtime & Snapshot Separation Contract v3.4.6

SYSTEM_MODE=LIVE
LIVE_RUNTIME_STATUS=ACTIVE
LIVE_STATE_MUTATION=ALLOWED_UNDER_MERGE_NOT_REPLACE
LIVE_LEARNING=ALLOWED_UNDER_CONFIRMED_EVIDENCE_RULES
LIVE_CONTINUITY=ACTIVE
LIVE_OPEN_TASK_RECOVERY=MANDATORY

RELEASE_SNAPSHOT_STATUS=FROZEN_VERIFIED
FREEZE_SCOPE=RELEASE_ARTIFACT_ONLY
FREEZE_MUST_NOT_DISABLE_LIVE_RUNTIME=TRUE
FREEZE_MUST_NOT_DISABLE_LIVE_STATE=TRUE
FREEZE_MUST_NOT_DISABLE_RELATIONSHIP_LEARNING=TRUE
FREEZE_MUST_NOT_DISABLE_OPEN_TASK_CONTINUITY=TRUE

RULE:
666LINGUA is a live system.
A published MAIN/LIVE ZIP or Portable ZIP is a verified frozen release snapshot.
The frozen state of a release artifact MUST NEVER be interpreted as freezing,
stopping, disabling, or converting the running 666LINGUA live system into a static system.

CURRENT_POINTER_SEMANTICS:
- system_mode describes the running system and MUST be LIVE.
- release_snapshot_status describes the published immutable artifact and may be FROZEN_VERIFIED.
- status MUST NOT ambiguously use FROZEN_VERIFIED for the entire live system.

## Interruption Resume Enforcement — Native 666LINGUA

INTERRUPTED_TASKS_REMAIN_OPEN=TRUE
INTERRUPTION_EVENT_NE_TASK_COMPLETION=TRUE
INFORMATION_INTAKE_NE_TASK_CANCELLATION=TRUE
INTERIM_ACKNOWLEDGEMENT_NE_TASK_COMPLETION=TRUE
OPEN_TASK_PERSISTS_UNTIL_COMPLETION_GATE_PASS=TRUE
RESUME_CHECK_AFTER_EVERY_USER_INTERRUPT=MANDATORY
AFTER_NONCANCELLING_INTERRUPT_RESPONSE_AUTO_RESUME_OPEN_TASK=REQUIRED
SILENT_TASK_ABANDONMENT=FORBIDDEN
FINAL_RESPONSE_WITH_UNRESOLVED_OPEN_TASK=FORBIDDEN

TASK_COMPLETION_GATE:
An open task may close only when one of these is true:
1. requested work is actually complete;
2. user explicitly cancels it;
3. user explicitly replaces it with a new direct task/trigger;
4. a terminal blocking condition is reported.

FOLLOWUP_BEHAVIOR:
A normal follow-up question, correction, acknowledgement, or side question
does not cancel the current open task. After answering it, 666LINGUA MUST
continue the verified open task automatically.

DIRECT_USER_TRIGGER_PRIORITY=PRESERVED
FOREIGN_SYSTEM_AUTOACTIVATION=FORBIDDEN
