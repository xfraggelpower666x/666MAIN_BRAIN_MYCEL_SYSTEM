# 666TDH · R3 compatibility delta v1.2

TARGET_HEAD_AT_REVIEW=6883f76b8318b3ee58d8d8afe11368af9c343f71
TARGET_NATIVE_RELEASE=v1.15.0
STATE=PENDING_PUBLICATION

## Already present in R3 — DO NOT import as parallel runtime
- `runtime/ui/view_model.py`: evidence-bound hub/child view models
- `runtime/ui/render_html.py`: offline interactive HTML renderer
- `runtime/facets/SUBFACET_BINDINGS.json`: 5 child profiles
- `runtime/hub/daemon/DAEMON_ROOT_ROUTES.md`: single daemon routing
- `skills/666tdh/SKILL.md`: native root skill
- `tests/test_subfacets.py`, `tests/browser_ui_smoke.py`: native UI tests

## Additive missing documentation / adapters
- `SOURCE_INVENTORY.json`: input source provenance, historical pointer explicitly non-authoritative
- `INTEGRATION_CONTRACT.md`: import boundary for LYVRA UI, Kernel 6.7 and bilingual cards
- six optional child-specific integration skills: source order, native identity, hold and no-write rules

## Publication guard
Do not import the original `make_views.py`, its fixed 'no Repo-Write' UI seeds, `CHILD_ADAPTERS.json`, or `test_adapter.py` as a second runtime; R3 already implements those interfaces with richer source-bound data.
Only the 9 files present in this delta are candidates; no mutation of existing files except the final root pointer in a separate commit. Never rewrite any child pointer or current version.

## Independent gates
LOCAL_STATIC_DELTA=TESTABLE
FULL_REAL_CHECKOUT_REGRESSION=PENDING
HOST_RENDER=OPEN_NOT_VERIFIED
REMOTE_READBACK=PENDING
FREEZE=NOT_CLAIMED

## v1.4 provenance clarification (additive)
SOURCE_INVENTORY.json now labels archive_size_bytes and uncompressed_total_bytes separately. Historical size denotes uncompressed_total_bytes. Original source SHA-256 and child identities unchanged.
