# 666StreamTranscoder v3.0

**Project identity:** 666StreamTranscoder v3.0  
**Repository path:** `PROJECTS/666StreamTranscoder/`  
**Base:** 3DX Radio Streamer 1.3.0 — preserved source, additive evolution.

## Preservation contract

The complete 3DX Radio Streamer 1.3.0 source is retained in `legacy/3dx-radio-streamer-1.3.0/`. The active project begins from the same source tree. Existing modules, dependencies, build scripts, tests, docs, assets, integrations, and operating workflows are preserved. Changes must be additive or demonstrably behavior-preserving.

## Current commit scope

- Complete 3DX 1.3.0 source baseline copied into this project.
- Original source snapshot retained under `legacy/3dx-radio-streamer-1.3.0/`.
- Active theme palette updated to the 666SOUNDsDESIGn cyber-neon direction (cyan / pink / purple with yellow warning accent).
- Original source and license notices retained.
- No Resin 2.0 code is silently substituted for the 3DX engine.

## Next additive implementation

1. Automatic playlist crossfade, configurable from 3 to 15 seconds (default 8 seconds).
2. Skip button requests an immediate crossfade into the prepared next queue item.
3. Crossfade runs inside the existing PCM mixer; the long-running encoder and stream socket must remain alive.
4. Preserve all existing broadcast, server, integrations, queue, microphone ducking, metadata, logging, setup wizard, and build paths.
5. Add Resin 3 capabilities as isolated modules with explicit integration points.

## Important status

This commit is the preserved source baseline and visual palette step. The automatic crossfade / skip integration and Resin 3 feature set are **not claimed as completed in this GitHub commit**. They require their own source changes and direct readback.

## Run

Use `Start-666StreamTranscoder.bat` on Windows after installing the requirements and FFmpeg as documented in the original project README under `legacy/3dx-radio-streamer-1.3.0/README.md`.
