# PSYLLO MYCEL R02 · Executable UI / Guidance Bridge Audit

DATE=2026-11-20
OWNER=666MAIN BRAIN MYCEL SYSTEM
BRANCH=666MAIN_BRAIN
SOURCE_HEAD_BEFORE_AUDIT=1257df656999c969cdadd3f8c2f033c11f7dbe73
PRECHANGE_RECOVERY=AUDIT/PRECHANGE_MYCEL_UI_DAEMON_ADAPTER_R02_2026-11-20.md
STATUS=SOURCE_AND_LOCAL_CLI_VERIFIED_HOST_PARTIAL

## In-scope body readbacks
BRIDGE=INTEGRATIONS/PSYLLO_CODING/workbench/scripts/mycel_bridge.py
BRIDGE_GIT_BLOB=47e7a1ebc972437ca302b7a3fdf4dafc8db56782
TEST_SOURCE=INTEGRATIONS/PSYLLO_CODING/workbench/tests/test_mycel_bridge.py
TEST_BLOB=e956d8390519f7e77ec074df966ac6961ec18869
RUNBOOK=INTEGRATIONS/PSYLLO_CODING/workbench/README_MYCEL_R02.md
RUNBOOK_BLOB=ae9b32b2ef5a1351990857189986cd4f8ee321d7
WORKBENCH_SKILL_BLOB=ef505270c6fb0c22100ec426b38799550333bf4e
WORKBENCH_README_BLOB=411a822211e4c71a1f89358506ba49c472ba34c1
INTELLIGENT_UI_CONTRACT_BLOB=6720d1a68a0096c7e0ee5e85db6134a9ca91c619
RUNTIME_REGISTRY_BLOB=3c13abb1091272fe42f223786fb2cfa6869572df

## Non-regression
EXISTING_RENDERER=INTEGRATIONS/PSYLLO_CODING/workbench/scripts/render_ui.py
RENDERER_BLOB_UNCHANGED=606c27e6b565996108deb4c3d263effd43184aec
MENU_SCHEMA=psyllo.intelligent-menu.1
DAEMON_STATE_SCHEMA=psyllo.guidance-state.1
NATIVE_UI_HANDOFF=psyllo.ui-handoff.1
EXISTING_WORKBENCH_HANDOFF=scevi.visual.handoff.1
NO_HANDOFF_SCHEMA_MERGE=TRUE
NO_FOREIGN_AUTOSTART=TRUE
NO_FOREIGN_REPOSITORY_MUTATION=TRUE
ORIGINAL_NATIVE_TRIGGERS_PRESERVED=TRUE

## Observed local tests
LOCAL_PYTHON_SOURCE_GIT_HASH=47e7a1ebc972437ca302b7a3fdf4dafc8db56782
LOCAL_PYTHON_COMPILE=PASS
LOCAL_UNIT_TESTS=10_OF_10_PASS
LOCAL_TEST_RUNNER=python -m unittest -q test_bridge_local.py
LOCAL_TEST_SOURCE=EQUIVALENT_SEMANTIC_SCENARIOS_NOT_REMOTE_CHECKOUT_REPO_TEST_FILE
LOCAL_CLI_SMOKE=PASS
LOCAL_CLI_EFFECT=JSON_PROJECTION_ONLY
LOCAL_HTML_RENDERER_EXECUTION=NOT_RUN
LOCAL_BROWSER_INTERACTION=NOT_RUN
WINDOWS_APP_ACCEPTANCE=NOT_RUN

Tested: six native menu view projection, valid matching view restore, wrong commit, wrong lineage, missing lineage, wrong owner, malformed SHA, forbidden menu action, missing blocker/action fallback, and project-key rejection. Local source was matched to the exact remote Git blob after hardening. Remote test file has been direct-read but its own unittest command was not executed against a full repository checkout in this run.

## Contradiction and authority audit
- All new R02 files and updated integration sources were fetched from current GitHub branch with direct SHA checks.
- Existing rendering engine is untouched; the new adapter provides its existing six-view JSON shape and companion projection.
- Daemon does not independently execute. A command in native menu is text-only unless the actual host explicitly presents and the user invokes a supported action.
- The newer unrelated repo commits are preserved without reverting their changes.
- No host/plugin release published; source integration does NOT equal delivery/adoption/host pass.
- The ten native MAIN BRAIN fresh-chat cases remain PENDING.
- 666DEV authoritative runtime/Windows source readback remains pending.
- Migration status remains IN_PROGRESS, Drive role MIGRATION_SOURCE_RECOVERY.
- New browser/renderer execution and plugin adoption require independent receipts.

NEXT=AUTHORIZE_SEPARATE_RELEASE_OR_HOST_ACCEPTANCE_AND_RUN_REPO_CHECKOUT_UNIT_SUITE
