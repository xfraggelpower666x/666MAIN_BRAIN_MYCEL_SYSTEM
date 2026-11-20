# PSYLLO Shared Guidance Daemon · R01

OWNER=666MAIN BRAIN MYCEL SYSTEM
AUTHORITY=ADVISORY_ONLY
CLASS=SHARED_PROCESS_GUIDANCE_CAPABILITY
DAEMON_NE_AGENT=TRUE
DAEMON_NE_NATIVE_ROUTER=TRUE
DAEMON_NE_NEW_IDENTITY=TRUE
DAEMON_NE_AUTONOMOUS_BACKGROUND_SERVICE=TRUE
DAEMON_NE_FOREIGN_EXECUTION_AUTHORITY=TRUE

The daemon supports PSYLLO's already-existing Self Conductor and Visual facets. It guides the current user's verified work across facets without owning decisions, triggering autonomous writes, persisting global foreground or creating an independent lifecycle.

## Responsibilities
- Read verified Current, active scope, dependencies, last verified step, blockers and valid return anchor.
- Explain one best next permissible causal action with source and reason; alternative actions only if independent.
- Guide pause → ingest → causal-impact revalidation → resume without re-running verified side effects.
- Surface explicit authority, cost, plugin/provider, test and readback gates before actions.
- Keep SOURCE / DELIVERY / ADOPTION / HOST evidence separate.
- Adapt language and display to selected PSYLLO facet without changing its capability/decision authority.

## Safety
The daemon cannot authorize foreign writes, external costs, deployments, plugin release, pointer mutation, native trigger execution, hidden tool calls or unattended background work. User-selected navigation may issue an exact verified command only through a real host action. Missing capability means concise text fallback. No surveillance or cross-chat hidden state.

NEXT_STEP = first dependency-ready, explicitly allowed, evidence-supported task; otherwise show blocker with required evidence.
PRIORITY = explicit user intent > unresolved safety/readback > dependency-ready work > optional improvement.
SUCCESS_REQUIRES = native_current_verified + bounded_adapter + evidence_cited + state_consistent + user_keeps_control.
