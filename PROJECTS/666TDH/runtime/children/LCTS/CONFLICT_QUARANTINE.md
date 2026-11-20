# Conflict Quarantine

This file records source ideas that are valid upstream but must not silently become LCTS authority.

## Q1 — Shortform final convergence
Upstream normal tracks may converge and terminate inside one render. LCTS must defer true closure until the Final Stage.

Disposition: `QUARANTINED_FROM_LONGFORM_DEFAULT`

## Q2 — Single-render duration surface
Suno generation controls are renderer-bounded. LCTS total runtime is not represented by one duration setting.

Disposition: `STAGE_BOUND_ONLY`

## Q3 — Normal Track Design output contract
The upstream visible package is optimized for a normal track build. LCTS requires a multi-stage package with state, anchors and validation.

Disposition: `NOT_IMPORTED`

## Q4 — Old production instructions inside source lyrics
Track-local old section, solo, drop, or instrument commands are not automatically authoritative for a new LCTS build.

Disposition: `SOURCE_MEANING_FIRST`

## Q5 — “More length = more events”
Rejected. Longform provides room for development, persistence, transformation and memory.

Disposition: `FORBIDDEN_SIMPLIFICATION`
