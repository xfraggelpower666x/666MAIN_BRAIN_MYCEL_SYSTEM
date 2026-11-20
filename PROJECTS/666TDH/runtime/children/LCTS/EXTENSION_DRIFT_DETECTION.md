# Extension Drift Detection

Review actual rendered audio after every extension.

## Drift channels
- TEMPO_DRIFT
- GROOVE_DRIFT
- KICK_DRIFT
- BASS_DRIFT
- GENRE_DRIFT
- IDENTITY_DRIFT
- ENERGY_RESET
- INTRO_RESTART
- UNWANTED_OUTRO
- VOCAL_RESET
- STORY_RESET
- MIXABILITY_LOSS
- PHRASE_BOUNDARY_DRIFT
- JOIN_SEAM
- PERCEIVED_SPEED_DRIFT

## Status

### SAFE
Extension continues the existing track and may proceed to transition review.

### REVIEW
Potential deviation exists; inspect against creator intent and whole-song context.

### REGENERATE_EXTENSION
Extension is musically interesting but breaks identity, story, motor, or continuity.

### ANCHOR_CHANGE_REQUIRED
The chosen source point biased the extension toward restart, ending, or instability.

### MANUAL_REPAIR_REQUIRED
The desired material is worth preserving but cannot be accepted through simple regeneration/anchor selection.

## Non-negotiable promotion principle
A musically exciting extension is not accepted when its low-end timing or track identity breaks.
