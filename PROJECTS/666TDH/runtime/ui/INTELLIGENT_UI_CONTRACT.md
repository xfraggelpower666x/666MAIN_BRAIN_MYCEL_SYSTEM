# 666TDH Intelligent UI and Menu — native view adapter R2

ROOT_AUTHORITY=PROJECTS/666TDH/CURRENT_POINTER.json
SOURCE_OF_CHILD_MENU=runtime/REGISTRY.json
SOURCE_OF_BRANCH_ACTIONS=runtime/TRIGGERS.json
SOURCE_OF_CHILD_UI_SECTIONS=runtime/facets/SUBFACET_BINDINGS.json
SOURCE_OF_NATIVE_VISUAL=runtime/hub/visual_adapters/<DIRECT_BRANCH_TOKEN>_VISUAL_ADAPTER.md
NO_FOREIGN_AUTOACTIVATION=TRUE
NO_FAKE_ACTION=TRUE
NO_UNVERIFIED_HOST_CLAIM=TRUE
VISUAL_AUTHORITY=NONE
RENDER_HOST_ACCEPTANCE=OPEN_NOT_VERIFIED

Hub menu: derive five child SYSTEMSTART commands and allowed hub commands
from current Registry/Triggers, never from archived START_MENU text alone.
Child menu: derive only the selected branch commands, add a return-to-Hub
copy action and child-specific UI panels. A button in exported HTML ONLY
copies an allowed direct command. It must never execute repo writes, navigate
external services or auto-start a child. All text insertion into DOM uses
textContent and the input JSON is escaped in its script container.

The view model contains a single advisory companion with evidence,
current task or an explicit unknown, a safe next action and a countercheck.
Session-only UI changes are not Current; no user selection grants update
or routing authority. For continuation, verify native root and selected
child first, then optionally apply a revision-bound user-supplied checkpoint.
