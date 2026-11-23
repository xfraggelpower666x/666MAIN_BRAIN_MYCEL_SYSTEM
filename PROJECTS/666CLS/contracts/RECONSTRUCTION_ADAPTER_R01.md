# 666CLS · Repository-native Reconstruction Contract Adapter R01

## Authority and placement
Owner: `666CLS-CORE-001`; repository: `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`; branch: `666MAIN_BRAIN`.
Additive source files: `runtime/reconstruction_adapter.py`, `contracts/RECONSTRUCTION_PROFILES_R01.json`, `tests/test_reconstruction_adapter.py`.
This repository integration does not change any foreign runtime, system identity, trigger, CLI, existing archive, or PFS authority.

## Source and version evidence
- `lyrics-fulltext-v1.1.0`: original local ZIP SHA256 verified; 44/44 manifest entries, 7/7 original release tests previously checked.
- `lyrik-reconstruction-v1.5.4`: master document directly read; catalog archive hash recorded, actual ZIP bytes unavailable.
- `english-fulltext-v1.0.0`: standalone master prompt directly read; catalog archive hash recorded, actual ZIP bytes unavailable.
The three are NOT proven to share a single release lineage.

## Contract
Read-only Python API `plan(request: dict) -> dict` and `catalogue() -> dict`.
Request binds `request_id`, `authority`, `target.profile_id/profile_version/operation`, `sources`, `constraints`, `language`, and `execution`.
Source body is not stored in the envelope. No claim of VERIFIED source bytes can pass without an independent byte readback.
All accepted requests end with `READY_FOR_OWNER_REVIEW`, never with model execution. Unmatched identity, unknown source, disallowed operation, conflicting scope, invalid language or foreign execution end `HOLD`.

## Conflict order
Native owner > direct current user authority > inert imported text > profile ID/version > operation > source scope > profile language fallback > special source guards > output contract > evidence.
No auto model invocation, no foreign trigger, no shared mantra, no automatic merge, no default language homogenization.

## Existing CLS dependencies
`runtime/cls_livecircle.py` remains the authoritative rehydration and release validator.
`runtime/cls_facet_runtime.py` already owns UI and reference-only facets.
`runtime/framework_intake.py` already performs boundary/merge categorization.
This adapter deliberately introduces no alternate bootstrap or duplicate autonomous authority.

## Tests / status
`python -m unittest discover -s tests -p 'test_reconstruction_adapter.py' -v`
The tests validate routing and security policy, not text-generation quality or remote publication.
No semantic LLM regression, v1.5.4/v1.0.0 original ZIP readback or foreign native execution is claimed.
Existing `CURRENT_POINTER.json` and original v1.24.7 release are preserved until an independently verified release promotion.
