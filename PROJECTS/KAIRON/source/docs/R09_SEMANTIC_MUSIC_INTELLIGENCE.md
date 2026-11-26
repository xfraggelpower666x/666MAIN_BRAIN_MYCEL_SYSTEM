# 666TDI v2.5 — R0.9 Semantic Music Intelligence

## Purpose
R0.9 improves the interpretation of creator intent from word matches toward explicit musical-function evidence. It asks what a phrase is intended to do in the arrangement, what it constrains, what it may collide with, and why a design decision is useful.

## Implementation
- `engine/semantic_intelligence.py` adds a deterministic, standard-library-only interpretation layer.
- It maps phrases to musical jobs (forward motion, low anchor, voice clarity, density, tension, release, recurrence, variation, contrast, spatial motion and finality).
- Negation is clause-local; the `avoid` field is always a constraint source, never positive support.
- Function collisions are explicit and remain potential until arrangement evidence or creator review clarifies them.
- A sequencing cue can downgrade a collision to `SEQUENCING_OR_ARRANGEMENT_MAY_RESOLVE`; it does not claim the collision is solved in audio.
- The module is pure/read-only and track-local. It does not mutate graphs, compile prompts, select presets, call a renderer or promote global rules.

## Why this matters
R0.7's pattern evaluator already used functional witnesses and counterrelations, but its signals included the `avoid` field and relied on substring/prefix matching. That could make a prohibited quality look like supporting evidence. R0.9 separates support from constraints and attaches an explanation to each interpreted musical job.

## Usage
After normal track analysis:
```bash
python -m engine.cli analyze <track_id>
```

The resulting `analysis.semantic_intelligence` object contains function evidence, potential collisions, decisions and limitations.

Focused inspection:
```bash
python -m engine.semantic_cli assess <track_id>
```

## Limits
This is an explainable rule-based semantic layer, not human-level understanding or an audio model. It cannot prove masking, groove, vocal intelligibility, emotional effect or renderer behavior. Ambiguous interpretation remains visible for creator review. Existing R0.8 audio measurement remains optional and separate.

## Preservation
R0.8 audio measurement, R0.7 pattern relations, the relational graph, renderer compiler, historical sources, existing tracks, identity and LiveCircle remain intact. No foreign repository or plugin is activated or modified.
