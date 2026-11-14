# Architecture — sunocleanser

**Language:** [Español](architecture.md) · [English](architecture.en.md)

## Modules

| Module | Responsibility |
|--------|----------------|
| `sunocleanser/audio/io.py` | WAV/MP3 input, WAV write (24-bit PCM), peaks |
| `sunocleanser/audio/stft.py` | STFT/iSTFT with length aligned to the original |
| `sunocleanser/suno/noise_profile.py` | Quiet frames (12%) and linked noise profile |
| `sunocleanser/suno/gain_mask.py` | Adaptive band mask, 7 dB ceiling, smoothing |
| `sunocleanser/suno/pipeline.py` | Orchestration, phase check, JSON report |
| `sunocleanser/cli.py` | Command-line interface |
| `sunocleanser/gui/app.py` | tkinter window; calls `process_suno_wav()` |

## Dependencies

- Python 3.11+
- NumPy, SciPy (`signal.stft` / `istft`)
- soundfile + libsndfile 1.2.2+ for WAV/MP3 decoding (Conda: `environment.yml`)

## Environment

```powershell
cd D:\progs\sunocleanser
conda env create -f environment.yml
conda activate sunocleanser
python -m sunocleanser.cli path\to\song.wav
```

## GUI

- `sunocleanser-gui.bat` / `sunocleanser-gui.sh` — `conda run` + `python -m sunocleanser.gui` (`.sh` may `source conda.sh` if conda is not on PATH)
- Or: `conda activate sunocleanser` and `python -m sunocleanser.gui`

Default output in `out/`. Processing runs on a background thread so the window stays responsive.
