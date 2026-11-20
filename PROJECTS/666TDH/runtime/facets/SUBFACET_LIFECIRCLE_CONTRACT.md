# 666TDH Subfacet LiveCircle Contract — Repo-Bindung R2

STATUS=REPO_CURRENT_BOUND
SYSTEM_ID=666TRACKHUB-001
OWNER=666TDH
NATIVE_ROOT=PROJECTS/666TDH
AUTHORITY_SOURCE=PROJECTS/666TDH/CURRENT_POINTER.json
DURABLE_MUTATION_ONLY=666TDH UPDATE
NO_NEW_CHILD_ROOT_AUTHORITY=TRUE
NO_SECOND_ROUTER=TRUE
NO_CHILD_UPDATE_TRIGGER=TRUE
NO_FOREIGN_AUTOACTIVATION=TRUE
NO_CROSS_SYSTEM_MERGE=TRUE
DAEMON_ROUTE_AUTHORITY=NONE
DAEMON_WRITE_AUTHORITY=NONE
SOURCE_VAULT_AUTOLOAD=FORBIDDEN

## Inheritance model

One root LifeCircle engine reads the current GitHub commit, root Current Pointer,
registry, scoped child Current Pointer, local state/visual bindings and continuity.
Each child has an **own logical sub-LiveCircle**, not a competing runtime owner.
Child declarations are separate and the engine is shared. Rehydrate root first,
then the directly selected child and only the child-local context; do not load
siblings' musical core files. Visual/daemon adapters are advisory only.

Subfacet lifecycle:
SELECTED_BY_DIRECT_USER_TRIGGER -> ROOT_CURRENT_VERIFIED -> CHILD_POINTER_VERIFIED
-> CHILD_SUBFACET_PROFILE_VERIFIED -> CHILD_REQUIRED_FILES_VERIFIED
-> CHILD_CONTINUITY_SCOPED -> UI_VIEW_MODEL_READY -> DAEMON_ADVISORY_READY
-> USER_ACTION / LOCAL_VIEW -> READBACK/FEEDBACK -> RETURN_TO_PARENT.

Failure: missing identity/version/hash => HOLD; wrong-branch handoff =>
CONFLICT_QUARANTINE; missing host capability => UI_FALLBACK; unresolved native
source identity => HOLD stays visible. Never infer success from a menu click.

## Subfacet contract fields

- `branch_token`: exact current Registry token
- `system_id`: exact child identity from Registry and Current
- `current_path`: existing child Current Pointer, unchanged
- `visual_adapter_path`: existing native child-specific adapter
- `local_subcircle`: state sequence / evidence gates, no second authority
- `local_rehydration`: required files and ordered dependencies
- `menu`: target-specific panels/actions from verified child contracts
- `daemon_guidance`: evidence-first recommendations, no auto-execution
- `continuity_scope`: child-only view/session checkpoint key
- `holds`: unresolved source-native identity, host evidence or private vault

## Host and session boundaries

The Hub can present native GPT UI or a text fallback. The CLI provides a
verified view model and cannot claim permanent ChatGPT background execution.
Child context can be carried in a user-supplied handoff, or persisted only by
an authorized 666TDH UPDATE. New session-local UI preferences are not current
runtime truth. The existing `continuity/CURRENT_HANDOFF.json` remains a
non-authoritative hub anchor; no foreign handoff may select a child.

## Executable companion

The root rehydration in `tdh.py` validates this contract and the profiles
before constructing target-native view models. `runtime/facets/lifecycle.py`
validates five child declarations and optional user-supplied session checkpoints.
`runtime/ui/view_model.py` composes root or selected-child menus and advisory
companion context; `runtime/ui/render_html.py` emits a local offline browser UI.
None of these components changes the root namespace, child current versions,
write permissions, music engines or external systems. Child UI controls copy
registered direct commands instead of silently executing them.

A root or child `SYSTEMSTART` remains read-only. A selected-child bootstrap
adds only its own current and native visual adapter. The existing parent
handoff is continuity-only and never selects a target. The original TD/LCTS
`NEW_CHAT_CONTINUITY.md` texts are preserved as historical child sources;
repo-native `tdh.py` returns the branch-scoped next-chat trigger.

`666TDH UPDATE` remains the only durable transaction. The root current
hashes all added implementation files. FSE and SHACHIVITI original source
identity remains `UNRESOLVED_HOLD`, and FSE source archive is vault-only.
Real interactive ChatGPT host acceptance remains OPEN_NOT_VERIFIED.
