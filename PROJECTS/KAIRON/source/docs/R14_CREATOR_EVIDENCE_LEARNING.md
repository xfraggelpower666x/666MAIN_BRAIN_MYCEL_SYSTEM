# 666TDI R1.4 – Creator Evidence Learning

## Authority and scope
- Native system: `666TDI-001` only; productive GitHub branch `666MAIN_BRAIN`, path `PROJECTS/666TDI/`.
- R0.9 semantic intelligence, R1.0 creative causal relationships, R1.1 visual daemon, R1.2 preanalysis and R1.3 device routes remain preserved.
- Coding Profi is a **coding-method coordinator**. LYVRA/CLIC/666DEV/MAIN BRAIN and Coder provide read-only guidance/skills; none are activated as a second TDI intelligence or given TDI write authority.

## Implemented
- `source/engine/creator_learning.py`: track-local, explicitly creator-confirmed outcome observations with category, decision ID, original intention, actual reported outcome, rating (SUCCESS/MIXED/UNSUCCESSFUL), optional file SHA256 and device route.
- A dedicated local storage namespace `source/runtime/creator_evidence/`, saved **only after** explicit creator confirmation and button click. Existing R0.8 evidence and historical feedback ledgers remain untouched. Writes use atomic replacement and in-process serialization. There are no silent network calls.
- Content-addressed evidence IDs and hash validation on readback. Hash checks detect accidental/tampered content without claiming external signature authenticity.
- Read-only per-track report groups judgments by decision and musical function. It preserves positive/negative contradictions instead of forcing one preferred conclusion.
- Even repeated same-track outcomes remain candidate observations; **no** global promotion, automatic training, audio causality proof or cross-system learning.
- `POST /api/feedback`: explicit local creator-confirmed write.
- `POST /api/learning/read`: read-only track-local report with evidence references.
- R1.4 Neon-Cyber UI feedback form, consent checkbox, category/decision selection, outcome field, optional artifact hash and contradiction cards.

## Evidence semantics
A creator rating means `CREATOR_REPORTED_OUTCOME`, not measured audio. File SHA256 is **supplied**, not independently calculated by the daemon; an empty SHA does not block subjective feedback. Contradictory creator observations trigger `CONTRADICTORY_OUTCOMES_REVIEW_REQUIRED`. One outcome triggers `SINGLE_OUTCOME_CANDIDATE`. Repeated observations trigger `REPEATED_TRACK_LOCAL_OBSERVATION_NOT_GENERALIZED`. A causal/renderer claim requires controlled evaluation beyond R1.4.

## Privacy and security
The daemon remains bound to `127.0.0.1`, accepts JSON with a size limit, rejects foreign origin, validates track names before local storage, and avoids logging submitted lyrics. Creator notes should not contain secrets. The storage is local to the running installation and is **not** synchronized to GitHub, LYVRA or Cloud storage. The local file hash is an integrity indicator, not a digital signature.

## Validation
Focused unit tests cover confirmation, persistence/readback, tampering, isolation, path guards, contradiction preservation and no auto-promotion. The local isolated module logic test passed 10/10 on 2026-11-23; exact post-publication suite and browser/host acceptance remain separately open until executed against that revision.

## Follow-up
Use real creator-reviewed audio outcomes to assess reproducibility, track/context dependence and competing explanations. Only explicit future native governance may authorize any integration of learned rules into structural music defaults.
