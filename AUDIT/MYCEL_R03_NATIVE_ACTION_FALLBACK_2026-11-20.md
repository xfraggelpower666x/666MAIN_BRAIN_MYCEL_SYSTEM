# MYCEL R03 · Native Menu Action Data & No-JS Text Fallback — Audit
DATE=2026-11-20
OWNER=666MAIN BRAIN MYCEL SYSTEM
BRANCH=666MAIN_BRAIN
BODY_HEAD_AT_AUDIT=fa5b7a53683698a7d07c5fc0b0e46b8ce46515b1
RECOVERY=AUDIT/PRECHANGE_MYCEL_R03_2026-11-20.md
STATUS=SOURCE_VERIFIED_HOST_AND_EXECUTABLE_REGRESSION_PENDING

## Changed existing carriers — direct repository readback
BRIDGE=INTEGRATIONS/PSYLLO_CODING/workbench/scripts/mycel_bridge.py
BRIDGE_BLOB=c0b83ad1255a0db2c677ad23b5f5a1fe0851292c
HTML=INTEGRATIONS/PSYLLO_CODING/workbench/assets/ui-template.html
HTML_BLOB=542f05486d3db673ccf3ed1158b4216a3781534a
TESTS=INTEGRATIONS/PSYLLO_CODING/workbench/tests/test_mycel_bridge.py
TESTS_BLOB=34e38e1a5d34dcd62c8e125309cb32a8d2aefe50
MENU_BLOB_UNCHANGED=372763e437729c6661b3110ae780218c00536c5a
RENDERER_BLOB_UNCHANGED=606c27e6b565996108deb4c3d263effd43184aec
RUNTIME_REGISTRY_BLOB=4c23072c1cdd7b31e22e5b37498a28b7cdcbe475

## Causal repair
CAUSE_A=R02 exposed none of the verified four native MENU_REGISTRY actions as Workbench action data.
REPAIR_A=Projector enforces exact four-trigger allowlist, requires direct user click flag and emits navigate/VORGESCHLAGEN text-only action suggestions.
NONEXECUTION=No native trigger submission or mutation by projected action; user must issue real direct current command.
CAUSE_B=R02 inserted a nonempty pseudo-blocker when there were no real blockers; renderer therefore classified action menu as BLOCKIERT.
REPAIR_B=Omit companion.blocker altogether on truly empty blockers; preserve genuine blockers.
CAUSE_C=HTML host had no standalone no-JavaScript text surface.
REPAIR_C=Append accessible noscript region before original style, with six menu labels and four exact text triggers. No fake live data.

## Verification
SOURCE_READBACK=PASS
CONTRACT_CHECKS=13_OF_13_PASS
REGISTERED_UNIT_TEST_CASES=14
REPO_CHECKOUT_UNIT_TEST_EXECUTION=NOT_RUN
BROWSER_REAL_CLICK_NAVIGATION=NOT_RUN
JAVASCRIPT_DISABLED_REAL_BROWSER_RUN=NOT_RUN
VALID_INVALID_HANDOFF_BROWSER_E2E=NOT_RUN
PLUGIN_HOST_FRESH_CHAT=NOT_RUN
MIGRATION_FINAL_GATE=OPEN
FOREIGN_SYSTEM_WRITE=NONE
NO_REPLACEMENT=TRUE

## Remaining acceptance
Run the actual committed `python -m unittest discover -s INTEGRATIONS/PSYLLO_CODING/workbench/tests -p test_mycel_bridge.py` on a pinned real checkout, generate HTML from source-bound state, verify all six click views and accessible text fallback in JS-disabled browser, verify valid/invalid revision+lineage, and inspect resulting host action semantics. Plugin release and native ten-trigger fresh-chat matrix remain separate. Do not claim freeze or host PASS without these receipts.
