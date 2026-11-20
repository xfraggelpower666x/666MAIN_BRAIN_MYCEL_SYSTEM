# Learning Pipeline State Machine v1.7.0

## Inputs

- correction candidate;
- human review feedback;
- regression test candidate.

## Required fields

`candidate_id`, `source_type`, `source_hash`, `scope`, `evidence`, `conflicts`, `privacy_class`, `authority`, `state`, `created_at`.

## Transition guards

- no evidence → `REJECTED`;
- unresolved scope → `HOLD_SCOPE`;
- identity or semantic conflict → `CONFLICT_QUARANTINE`;
- personal data beyond minimum → `PRIVACY_REPAIR_REQUIRED`;
- human authority required but absent → `HUMAN_REVIEW_REQUIRED`;
- test failure → `REJECTED_TEST_FAILURE`;
- pass → `DEVELOPMENT_CANDIDATE` only.
