# HANDOFF · 666 RESEARCH MD DATABASE ORCHESTRA

**Active Release:** v1.7.0  
**Parent Release:** v1.6.0  
**State:** READY  
**System Audit:** 100% PASS · APPROVED  
**Primary Orchestrator:** `AudioResearchV17Orchestrator`

## New Active Branches

1. Automatic real-stem masking analysis
2. Preset compatibility matrix
3. Blind Suno A/B test system
4. 4D trajectory library for all 18 FX objects
5. Sonification-to-audio-upload pipeline

## Measured Validation

```text
JavaScript tests: 232 / 232
Python audio self-tests: 2 / 2
Feature checks: 160 / 160
Release gates: 136 / 136
Topics: 18
Prompts: 22
Blockers: 0
Warnings: 0
```

## Real-Stem Boundary

No user-generated stems were supplied during construction. The analyzer is executable and validated with deterministic synthetic fixtures. A real track report must only be created after aligned stems are placed in `input/stems` and processed by the Python analyzer.

## Restore and Verify

```bash
pip install -r requirements-audio.txt
npm run build
```

## Run Real Stem Analysis

```bash
python3 tools/stem_masking_analyzer.py \
  --input input/stems \
  --output output/stem-analysis
```

## Render Sonification Reference Audio

```bash
python3 tools/sonification_audio_pipeline.py \
  --input input/sonification/example-chaos.csv \
  --output output/sonification-upload \
  --columns x,y,z
```

## Restore Order

1. `MASTER_PROMPT.md`
2. `HANDOFF.md`
3. `docs/system/V1_7_0_AUDIO_PIPELINE_CAPTURE_REGISTER.md`
4. `system/config/system-manifest.js`
5. `system/bootstrap-loader.js`
6. `system/core/*.js`
7. `system/modules/*.js`
8. `data/topics/*.js`
9. `data/prompts/*.js`
10. `requirements-audio.txt`
11. `npm run build`
12. `output/SYSTEM_AUDIT.md`
