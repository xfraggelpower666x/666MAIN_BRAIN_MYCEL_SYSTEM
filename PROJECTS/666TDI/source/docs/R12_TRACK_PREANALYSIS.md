# 666TDI R1.2 – Track Pre-Analysis Intelligence

## Current and provenance
R1.2 extends the local 666TDI R1.1 visual daemon. The musical source of authority remains R1.0 Creative Causal Emergence, which itself consumes R0.9 Semantic Music Intelligence. No parallel composing engine or foreign LYVRA runtime was introduced.

## Implemented
- Eight **proposed** musical chapters, each displaying role, reason, R0.9 function witnesses, qualitative energy shape and review status.
- Optional explicit 4/4 bar target (32–2048). No silent default. Exact integer allocation with largest remainder, zero-based start and exclusive end markers.
- **Theoretical** duration calculated only when both bar target and BPM are explicitly provided. It is not a guarantee of actual Suno duration.
- LOW/MID/HIGH/VOICE intent and musical-role matrix, reflecting only user-provided fields and R0.9 supported witnesses.
- Function relations sourced from R1.0; alternatives derived from R1.0 emergences, showing preserve vs change and the effect/tradeoff.
- New Neon-Cyber timeline, chapter evidence, layer cards and alternatives in the existing R1.1 UI.
- All new findings included in the existing local JSON handoff; device preflight still required before assessment.

## Explicit limits
No inferred planetary plot points or song-specific scenes; no invented motives. Chapter names and relative-energy indicators are proposed design scaffolding, not outputs of an audio measurement, actual notes, or rendered track prediction. A chapter without supporting function evidence is marked optional. No automatic changes to Suno, renderer, R1.0, R0.9, stored tracks or global learning.

## Implementation references
- source/engine/track_preanalysis.py
- source/engine/daemon_cli.py
- source/engine/daemon_static/index.html
- source/tests/test_track_preanalysis.py
- facets/daemon/CONTRACT.json

## Start
From source:
```bash
python -m engine.daemon_cli --port 8766
```
Open http://127.0.0.1:8766. Choose iPhone Suno App or PC Suno Browser, describe the musical intent, optionally specify planned bars, and run the preanalysis.

## Validation
Focused tests are authored. Python execution and native visual host acceptance must be reported separately from GitHub blob integrity. In particular the proposed energy graph and timeline are visual hypotheses, not actual measurements.

## Next steps
R1.3 verified device-specific rendering routes, while keeping common musical reasoning shared; R1.4 creator-feedback learning remains evidence-bound.
