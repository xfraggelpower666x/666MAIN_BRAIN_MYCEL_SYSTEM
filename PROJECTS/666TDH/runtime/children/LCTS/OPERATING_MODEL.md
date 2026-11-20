# Operating Model

## Operating principle

LCTS is not a “make a very long song” prompt generator. It is a stage-aware composition system.

Each stage asks:
- What identity already exists?
- What motor has the listener learned?
- What has the story already said?
- Which motifs now carry memory?
- What pressure is unresolved?
- Why should the track continue?
- What may change without making a new song?
- Where can the next Extend attach without inheriting an ending gesture?

## Modes

### PLAN
Create Track Manifest, target runtime, stage map, story arc, motor and first anchor strategy.

### BUILD_BASE
Create the Base Generation package and its Continuation Zone.

### REVIEW_STAGE
Evaluate rendered audio against state and drift criteria.

### BUILD_EXTEND
Build the next extension package using the accepted Whole Song state.

### FINALIZE
Create Final Stage only when the planned journey is ready to end.

### RECOVER
Rehydrate from Track Manifest + Continuity State + latest accepted Stage Review + Extend Map.

## State rule

`FOUND != VERIFIED`

A stage becomes continuity authority only after it has been listened to and accepted.
