# R05 Active Build — Manual Catalog Classification

BASE_HEAD=d6b3dde6add02c51d4b0e800a436c3ea5bd4d8d8
SCOPE=PROJECTS/666_FULL_LYRICS_INTELLIGENCE/
CHANGE_KIND=ADDITIVE_FEATURE
USER_REQUEST=NO_MORE_TEST_RUNS_ACTIVE_BUILD
TESTS_EXECUTED_THIS_CHANGE=NONE
WINDOWS_GUI_ACCEPTANCE=OPEN

## Implemented
- `engine/bridge.py`: `correct_record` updates only project, category and title for the chosen existing record, retaining content and source hash; materializes current JSON and rebuilds the project index.
- `electron/main.cjs`: protected IPC action `catalog:correct`.
- `electron/preload.cjs`: allowlisted renderer method.
- `renderer/index.html`: metadata editor next to the full-text browser.
- `renderer/app.js`: loads current fields and saves deliberate user edits.

## Boundaries
No private database uploaded; no migration or alteration of R02 source. No CI, packaging, install, benchmark or Windows tests executed. Project code and status only.
Result is `SOURCE_PUBLISHED_RUNTIME_UNVERIFIED`, not production released.

## Next product construction
Build bulk selection / mass-project assignment, editable topic taxonomy, review inbox and direct chat-backup JSON import adapters. Preserve existing functions.
