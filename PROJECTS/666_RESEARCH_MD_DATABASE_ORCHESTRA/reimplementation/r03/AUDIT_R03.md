# R03 · Implementation Audit / Repair / Re-Audit

**Project:** 666 RESEARCH MD DATABASE ORCHESTRA  
**Scope:** `reimplementation/r03/` only  
**Version:** `0.3.0`  
**Status:** `VERIFIED_LOCAL_CANDIDATE`  
**Historical release:** `v1.7.1-clean-system.1` remains `READBACK_PENDING`.

## Source basis

- Current historical file manifest lists `tools/stem_masking_analyzer.py` with SHA-256 `5dce90b0dcc4896b2db5223d13415118ab9a4e7ceed7440d967d236bda261515`.
- The original analyzer is absent from the current Research Orchestra project tree; direct GitHub path readback returned `NOT_FOUND` and the repository path history query returned zero commits.
- The historical audit documents the six roles, strict role parser, duration mismatch guard (>1 second), bounded audio memory, and metrics including peak, RMS, stereo, band energy, transient and pairwise overlap.
- The historical handoff states that no real user stems were supplied and that the original analyzer was tested with synthetic fixtures only.
- R03 therefore uses a new versioned path and does not claim historical recovery.

## Implemented controls

| Area | Implementation | Status |
|---|---|---|
| Role parsing | Exact allowlist: kick, bass, vocal, acid, guitar, fx | PASS |
| File boundary | Relative paths only; traversal and symlink escapes blocked | PASS |
| Duplicate inputs | Same source file cannot be assigned to multiple roles | PASS |
| WAV format | Integer PCM 8/16/24/32-bit only; 1–2 channels | PASS |
| Sample rate | 8–96 kHz and common sample rate required | PASS |
| Duration | 600-second limit; >1-second mismatch blocks | PASS |
| Alignment | Common overlap explicit; excluded tail reported | PASS |
| Memory strategy | One stem at a time, 16,384-frame blocks, no whole-file load | PASS (code + fixture tests) |
| Resource guards | 2 GiB aggregate file-size guard and 32 MiB estimated working-set guard | PASS (negative tests) |
| Spectral analysis | Eight frequency bands, dBFS energy and relative shares | PASS (synthetic fixtures) |
| Pairwise analysis | Shared spectral share, relative level and heuristic pressure | PASS (synthetic fixtures) |
| Stereo / clipping / transient | Correlation, clipping count, p95/median RMS proxy | PASS (synthetic fixtures) |
| Provenance | SHA-256 of analyzed audio bytes per stem | PASS |
| Report write | Explicit output only, atomic write, no silent overwrite | PASS |
| LUFS / BS.1770 | Not implemented; no false LUFS claim | OPEN by design |
| Real user stems / host | No real input or production host acceptance | OPEN |

## Local verification evidence

Environment:

- Python `3.13.5`
- NumPy `2.3.5`
- Node.js `22.16.0` is present but not used by R03

Commands:

```bash
cd reimplementation/r03 && python -m unittest discover -s tests -v
python -m compileall -q .
python cli.py --help
```

Observed regression: **32/32 PASS**. The first run had one assertion wording mismatch between the test and the method disclaimer; the disclaimer was made explicit and the full suite was rerun. Final result: 32 tests passed, 0 failed.

A separate synthetic performance smoke used six 20-second mono PCM stems at 48 kHz (15 pair comparisons, 59 FFT windows per stem). Analysis completed in **0.231 seconds** in this container. Process maximum RSS was **121,848 KiB**; the post-import baseline was **95,372 KiB**, so the observed incremental peak was approximately **26,476 KiB**. This is one Linux-container observation, not a Windows-host or cross-platform memory guarantee.

Coverage includes valid two- and six-stem analysis, same-band vs separated-band overlap, all four integer PCM widths, stereo anti-phase, clipping, sample-rate and duration mismatch, one-second alignment tolerance, malformed/truncated WAV, path traversal, symlink escape, duplicate roles and files, size and memory guards, output overwrite protection, stdout/CLI behavior, and JSON finite-value serialization.

## Limitations

- No actual user-generated stems were available; synthetic audio validates implementation behavior only.
- The 32 MiB value guards the bounded analysis working-set estimate; it is not a hard OS memory limit. The observed synthetic process RSS includes the Python/NumPy runtime baseline and is recorded separately above.
- Masking pressure is a transparent heuristic, not a psychoacoustic threshold model.
- dBFS is reported; integrated LUFS/BS.1770 is not implemented.
- Only PCM WAV is supported; no MP3/FLAC/OGG decoding or FFmpeg process launch.
- This is local test evidence only. GitHub commit and provider readback must be recorded separately after publication.

## Decision gate

`R03_LOCAL_SOURCE_AND_TESTS_VERIFIED · HISTORICAL_ORIGINAL_READBACK_PENDING · REAL_STEM_HOST_TEST_OPEN · NO_PRODUCTION_FREEZE`.
