# System Architecture

LCTS consists of six functional layers. These are conceptual responsibilities, not separate autonomous systems.

1. **Identity & Scope**
   - confirms LCTS-only authority;
   - protects source system boundaries.

2. **Track Continuity State**
   - persistent session truth;
   - records motor, identity, story, motifs, stage history and next direction.

3. **Longform Composer**
   - decides what remains stable and what may evolve;
   - creates Stage A, intermediate Extend stages and Final Stage.

4. **Anchor & Whole-Song Operator**
   - prepares continuation zones before Extend;
   - selects safe Extend anchors;
   - governs Get Whole Song cycles.

5. **Drift & Validation**
   - evaluates audio after every generation/extension;
   - blocks interesting-but-invalid extensions from becoming Whole Song.

6. **Recovery**
   - rebuilds session context from files;
   - does not depend on chat memory.

## Authority flow

`TRACK_MANIFEST + CONTINUITY_STATE + CREATOR_SOURCE`
→ understand current relation
→ compose current stage only
→ render externally
→ review actual audio
→ accept/reject
→ update CONTINUITY_STATE
→ next stage

No stage is promoted merely because it exists.
