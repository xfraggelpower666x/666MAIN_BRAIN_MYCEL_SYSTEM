# 666 RESEARCH MD DATABASE ORCHESTRA · R03 Stem / Psychoacoustic Analysis

**Version:** `0.3.0`  
**Status:** `VERIFIED_LOCAL_CANDIDATE`  
**Identity:** `NEW_SEPARATE_IMPLEMENTATION` — not the missing historical v1.7.1 analyzer.

R03 is a separate, editable Python implementation under `reimplementation/r03/`. It does not replace R01/R02 or write to historical paths. It analyzes explicitly mapped WAV stems, calculates bounded spectral-band measurements, and produces transparent pairwise overlap indicators.

## Install

From this directory:

```bash
python -m pip install -r requirements.txt
```

Only NumPy is required for the bounded FFT windows. No SciPy, librosa, FFmpeg, network service or paid API is used by R03.

## Run from the Research Orchestra project root

```bash
python reimplementation/r03/cli.py \
  --input input/stems \
  --stem kick=kick.wav \
  --stem bass=bass.wav \
  --stem vocal=vocal.wav \
  --stem acid=acid.wav \
  --stem guitar=guitar.wav \
  --stem fx=fx.wav \
  --output output/stem-analysis
```

The `--stem ROLE=FILE` option is repeatable. Roles are exact and case-sensitive: `kick`, `bass`, `vocal`, `acid`, `guitar`, `fx`. Use at least two and at most six different roles. Filenames must be relative to `--input`; absolute paths, `..` traversal, path escapes and duplicate source files are rejected.

Without `--output`, the JSON report is printed to stdout and no report file is created. With `--output`, R03 writes `stem-analysis-r03.json` atomically into that directory. Existing reports are not overwritten unless `--force` is supplied. The output directory must not be inside the input-stem directory.

## Input and resource contract

- Uncompressed integer PCM WAV only: 8-, 16-, 24- or 32-bit.
- Sample rate: 8,000–96,000 Hz; mono or stereo.
- Two to six distinct stem roles.
- Maximum duration: 600 seconds per stem.
- All stems must use the same sample rate.
- Duration difference above 1.0 second blocks analysis. A difference at or below 1.0 second uses the explicit common overlap; every excluded tail is reported per stem. No silent alignment trim.
- Aggregate input size limit: 2 GiB.
- FFT window: 16,384 frames, one stem at a time. Source files are read in bounded blocks, never loaded whole into memory.
- The 32 MiB working-set guard is a conservative algorithmic estimate for NumPy buffers, not an operating-system RSS quota.

MP3, FLAC, OGG, floating-point WAV and compressed WAV are not accepted. Convert them to integer PCM WAV separately before analysis; R03 does not launch external converters.

## Measurements

Per stem:

- sample-based RMS, peak and crest factor in dBFS (not LUFS)
- clipping sample count and percentage
- stereo correlation and a negative-correlation mono-compatibility warning
- transient proxy: 95th-percentile window RMS divided by median window RMS
- energy and relative share in eight bands: 20–60, 60–120, 120–250, 250–500, 500–2,000, 2,000–5,000, 5,000–10,000 and 10,000–20,000 Hz
- SHA-256 of the audio bytes actually analyzed, plus explicit duration-tail accounting

Pairwise:

- shared spectral-share overlap
- overall and per-band level differences
- heuristic masking-pressure index and potentially masked role

**Important:** The masking-pressure index is an explainable heuristic: spectral-share overlap multiplied by a relative-level pressure factor. It is not a validated critical-band or simultaneous-masking-threshold model. It must not be interpreted as a scientific masking threshold. R03 does not claim ITU-R BS.1770 integrated loudness or LUFS; it reports dBFS.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests generate deterministic synthetic WAV fixtures in temporary folders. No user stems, audio files or generated reports are committed to this repository.

## Boundaries / next work

- Synthetic fixtures prove code paths only; no real user-stem report has been run.
- Actual host-side media selection, neutral audio delivery for blind A/B, and end-to-end Windows acceptance remain open.
- Historical v1.7.1 `tools/stem_masking_analyzer.py` remains unavailable in the current source tree. Its manifest hash is preserved as evidence; R03 is not represented as a byte-recovered original.
- LUFS/BS.1770, perceptual critical-band masking and reference-calibrated thresholds require a separately validated implementation and fixtures before being added.
