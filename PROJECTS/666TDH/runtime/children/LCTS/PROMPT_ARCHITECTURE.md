# Prompt Architecture

LCTS outputs stage-specific packages rather than one giant prompt.

Minimum package:
1. `01_TITLE`
2. `02_MASTER_STYLE`
3. `03_BASE_GENERATION`
4. `04_BASE_LYRICS_STRUCTURE`
5. `05_CONTINUATION_ZONE`
6. `06_EXTEND_STAGE_B`
7. `07_STAGE_B_LYRICS_STRUCTURE`
8. `08_EXTEND_STAGE_C`
9. `09_STAGE_C_LYRICS_STRUCTURE`
10. `10_FINAL_STAGE`
11. `11_FINAL_LYRICS_STRUCTURE`
12. `12_DJ_MIX_GUIDE`
13. `13_EXTEND_MAP`
14. `14_VALIDATION`

For additional extensions, add numbered stage packages.

## Prompt compression principle
The system documentation stores architecture.
The renderer prompt stores only current stage necessities.

Every Extend prompt restates enough to preserve:
- engine target;
- BPM;
- core motor;
- current track identity;
- previous accepted state;
- current stage goal;
- no-restart relation;
- continuation or finalization intent.

It does not repeat the whole handbook.
