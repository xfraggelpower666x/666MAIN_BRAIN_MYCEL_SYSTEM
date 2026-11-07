# LINEAGE-AWARE CONTINUITY

OWNER=666MAIN BRAIN MYCEL SYSTEM
TRIGGERS=666MAIN BRAIN NEW CHAT|666MAIN BRAIN NEXT CHAT

## Principle

Never use global-latest handoff. Continuity is scoped to verified lineage, workspace/scope and return anchor.

## Handoff fields

HANDOFF_ID
LINEAGE_ID
SOURCE_SCOPE
TARGET_SCOPE
RELATED_SYSTEM_CARD
LAST_MEANINGFUL_EXCHANGE
CURRENT_INTENT
APPROVED_WORK
DISCUSSED_ONLY
OPEN_QUESTIONS
ACTIVE_STRANDS
INTERRUPTIONS
RETURN_ANCHOR
SOURCE_HEAD
SOURCE_POINTER
PROVENANCE
SUPERSESSION
PERSISTENCE_STATUS

## Create-first persistence

On NEW CHAT:
1. read fresh current pointer and HEAD;
2. resolve current lineage;
3. if no lineage exists, allocate a new non-colliding lineage ID;
4. existence check target path;
5. verify expected HEAD;
6. create immutable handoff;
7. immediate full readback;
8. mark PERSISTED only after readback.

On NEXT CHAT:
1. rehydrate Whole MAIN BRAIN first;
2. resolve explicit lineage;
3. read exact handoff;
4. verify supersession/provenance;
5. restore relevant scope and return anchor;
6. keep related systems RELATED_ONLY until direct user foreground intent.

GLOBAL_LATEST_HANDOFF=FORBIDDEN
HANDOFF_NE_AUTHORITY=TRUE
PERSISTED_REQUIRES_DIRECT_READBACK=TRUE
