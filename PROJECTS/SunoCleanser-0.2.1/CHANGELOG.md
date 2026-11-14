# Changelog

## 0.2.1 — path collision repair
### Fixed
- Check Clean WAV, Removed Noise WAV and JSON report paths against the input and
  each other before writing any file. Detect aliases through symlinks and existing
  hard links.
- Validate the entire CLI batch before processing its first input. Conflicting
  paths abort with exit code 5, preserving the inputs and any earlier results.
- Keep the existing output filenames and DSP processing for valid paths.

### Verification
- Linux, Python 3.12.14 and the versions in `requirements.lock`: all 19 existing
  tests and all 5 path collision regression tests passed. All 5 new tests
  reproduced the defects on 0.2.0.
- Windows GUI: create the `sunocleanser` Conda environment as described in the
  README and open `sunocleanser-gui.bat`. Windows launch and interactive GUI
  verification remain open.

## 0.2.0 — frozen release
### Fixed
- Packaging: `pip install .` / `pip install -e .` produced `ModuleNotFoundError: No module named 'src'`
  (package renamed `src` → `sunocleanser`, `[build-system]` and package discovery added).
- Phase-cancel verification was tautological (always ≈ −300 dB). It now reads the written 24-bit
  files back and null-tests `original − noise` against `clean`, in dBFS.
- Crash on inputs shorter than `n_fft` and on files with more than 2 channels.
- Output could overwrite the input file (e.g. input named `… - Removed Noise.wav`).
- GUI output folder no longer depends on the working directory when `SUNOCLEANSER_OUT` is set (default stays `./out`).
- README typo ("líea").

### Added
- N-channel support (channel-linked noise profile and shared gain mask; mono and stereo unchanged).
- Input validation with clear errors (`InvalidInputError`, CLI exit code 5): empty/short/non-audio/NaN files, invalid parameters, NOLA check.
- Report: `tool_version`, `input_sha256`, `clipped_samples`, per-channel peaks.
- CLI: batch mode (several files), `--bass-cut`, `--oversubtraction`, `--threshold-db`, `--quiet`, `--version`.
- Tests: 1 → 19 (null-test sensitivity, mono, 6 channels, silence, 48 kHz, short/invalid input, overwrite guard, CLI exit codes, batch).

### Known limits
- The tkinter GUI was syntax-checked but not run in the audit environment (no tkinter there).
- Clipping beyond full scale is reported and fails verification; no automatic gain reduction (by design: no normalization).
