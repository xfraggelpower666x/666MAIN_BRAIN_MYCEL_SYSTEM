# 666LINGUA State Merge and Rehydration Contract v3.4.6

STATE_WRITES_ARE_MERGES=TRUE
PROFILE_UPDATE_MODE=MERGE_NOT_REPLACE
HANDOFF_UPDATE_MODE=MERGE_NOT_REPLACE
RELATIONSHIP_LEARNING_UPDATE_MODE=MERGE_NOT_REPLACE
COMPACT_PROFILE_OVERWRITE=FORBIDDEN

Before every confirmed state change:
READ current state
→ MERGE only confirmed changes
→ PRESERVE confirmed preferences
→ PRESERVE unknown non-deprecated fields
→ VALIDATE
→ WRITE
→ READBACK
→ CHECKPOINT

SYSTEMSTART:
READ CURRENT_STATE_POINTER
→ REHYDRATE profile
→ REHYDRATE handoff
→ REHYDRATE relationship learning
→ REHYDRATE temporal profile
→ only ask for fields that are truly unresolved

The user profile and relationship-learning state are complementary.
Neither may silently erase information held by the other.
