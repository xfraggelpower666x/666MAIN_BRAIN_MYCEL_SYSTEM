# PARALLEL DEPLOYMENT

PARALLEL_DEPLOYMENT_OWNER=666MAIN BRAIN MYCEL SYSTEM
SCHEDULER=PSYLLO_CHAOS_CONDUCTOR
MODE=WORK_CONSERVING_CAUSAL_PARALLELISM

## Core rule

Use the maximum useful number of independent strands. Each strand processes the maximum safe amount of work until it reaches a dependency, authority, lock, readback or pointer barrier.

MAX_STRANDS=DYNAMIC_BY_INDEPENDENCE
MAX_TASKS_PER_STRAND=UNTIL_REAL_BARRIER
ARTIFICIAL_SERIALIZATION=FORBIDDEN
UNSAFE_SHARED_WRITE_CONCURRENCY=FORBIDDEN

## Strand lifecycle

DISCOVER
→ SPLIT_BY_CAUSAL_INDEPENDENCE
→ ASSIGN_SCOPE
→ VERIFY_AUTHORITY
→ PROCESS_MAX_SAFE_TASK_BATCH
→ READBACK
→ RETURN_EVIDENCE
→ MERGE_ONLY_COORDINATION_RESULTS
→ CHECKPOINT

## Write serialization

Independent reads, audits, catalog analysis, card enrichment and non-overlapping source creation may proceed concurrently.

Writes touching the same:
- current pointer
- registry row
- lock
- canonical state file
- authority document
- shared system card

must serialize.

## Work-conserving interruption rule

If one strand blocks:
- continue every independent strand;
- process new user information immediately;
- recompute only affected dependencies;
- return to the blocked strand when its blocker changes.

## No simulation

SIMULATED_STRAND_COMPLETION=FORBIDDEN
FAKE_PROGRESS=FORBIDDEN
PLANNING_NE_EXECUTION=TRUE
REAL_ARTIFACT_OR_VERIFIED_STATE_REQUIRED_FOR_DONE=TRUE
