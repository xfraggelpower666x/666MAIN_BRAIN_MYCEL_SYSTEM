# 666TDI v2.5 — R0.5 Relational Music Intelligence

STATUS: LOCAL_IMPLEMENTED / MUSIC_INTELLIGENCE_PARTIAL

## Preserved
R0.4 is the only current baseline. `engine/portable.py`, the original renderer compiler, feedback functions, character `666TDI` (er/ihn), original local LiveCircle and archival evidence remain unchanged. The new module is `engine/relational.py`; its CLI is `engine/relational_cli.py`. Local storage: `runtime/relations/<track_id>.json`.

## Implemented
- Track-scoped causal graph with nodes, edges, provenance and idempotent building.
- Relation types include CAUSES, CONSTRAINS, SUPPORTS, CONFLICTS, TRANSFORMS, RETURNS_WITH_HISTORY and TRANSLATES_TO.
- Track-design review highlights undefined motor/ending and potential voice/MID conflicts, without pretending to diagnose actual masking.
- Renderer outcomes are saved per renderer and per track with provenance. Measured-audio labels require an artifact reference.
- Cause attribution requires evidence and review, while UNKNOWN remains a hypothesis. No outcome promotes a global rule automatically.
- Rehydration checks graph integrity, edges, system ID and underlying LiveCircle status.

## Limits
Graph creation uses explicit text fields and predefined causal relationships; this is a deterministic engineering substrate, not an LLM semantic composer. It does not analyze waveforms, listen to sound, modify renderer prompts automatically or train models. Edge evidence is not auditory validation. Full musical intelligence, contextual card activation with counterexamples, listener evaluations, true stem masking analysis, and independently verified provider behaviour remain open.

## Test evidence
`python -m unittest discover -s tests -v` — 45/45 successful in Python 3, local temporary test directories for new graph tests. Tests do not touch foreign repositories.

## CLI
```bash
python -m engine.relational_cli build <track_id>
python -m engine.relational_cli inspect <track_id>
python -m engine.relational_cli assess <track_id>
python -m engine.relational_cli rehydrate
```

## Source separation
The design is a native 666TDI local derivative of R0.4 and historical observations. Historical LYVRA source is archival evidence, never authority. No autonomous GitHub writes, no automatic chat trigger installation.

## Next executable development
Add creator-reviewed relevance/counterevidence to card activation and controlled renderer A/B comparison with real uploaded audio.
