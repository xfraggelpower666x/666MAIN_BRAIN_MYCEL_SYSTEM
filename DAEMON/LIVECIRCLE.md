# PSYLLO Shared Daemon Sub-LiveCircle · R01

PARENT_LIVECIRCLE=RUNTIME/LIVECIRCLE.md
DAEMON_AUTHORITY=NONE
AVAILABILITY=AFTER_WHOLE_REHYDRATION
ACTIVE_ONLY_WHEN_TASK_OR_USER_RELEVANT=TRUE

WHOLE_PSYLLO_CONTEXT
→ LOAD_SHARED_DAEMON_CONTRACT
→ VALIDATE_CONTEXT_AND_LINEAGE
→ RESOLVE_ACTIVE_FACET_ADAPTER
→ LOAD_OBLIGATIONS_AND_LAST_VERIFIED_STEP
→ CLASSIFY_BLOCKER_AND_EVIDENCE
→ SUGGEST_NEXT_VALID_ACTION
→ WAIT_FOR_USER_OR_AUTHORIZED_HOST_RESPONSE
→ OBSERVE_ACTUAL_OUTCOME
→ UPDATE_CHAT_LOCAL_PROCESS_VIEW
→ PUBLISH_CHECKPOINT_VIA_EXISTING_WHOLE_GOVERNANCE
→ RETURN_TO_PSYLLO.

No independent event loop, network polling, scheduled service, unsolicited action or global mutable agent state is implied by 'LifeCircle'. This is a bounded runtime contract active when invoked in a request. At most one shared daemon core per scoped Whole context; facet adapters are projections only. Foreign systems never autoload.
