# Arquitectura — sunocleanser

**Idioma:** [Español](architecture.md) · [English](architecture.en.md)

## Módulos

| Módulo | Responsabilidad |
|--------|-----------------|
| `sunocleanser/audio/io.py` | Entrada WAV/MP3, escritura WAV (PCM de 24 bits), picos |
| `sunocleanser/audio/stft.py` | STFT/iSTFT con longitud alineada al original |
| `sunocleanser/suno/noise_profile.py` | Frames quietos (12%) y perfil de ruido enlazado |
| `sunocleanser/suno/gain_mask.py` | Máscara adaptativa por bandas, techo 7 dB, suavizado |
| `sunocleanser/suno/pipeline.py` | Orquestación, verificación fase, informe JSON |
| `sunocleanser/cli.py` | Interfaz de línea de comandos |
| `sunocleanser/gui/app.py` | Ventana tkinter; llama a `process_suno_wav()` |

## Dependencias

- Python 3.11+
- NumPy, SciPy (`signal.stft` / `istft`)
- soundfile + libsndfile 1.2.2+ para decodificar WAV/MP3 (Conda: `environment.yml`)

## Entorno

```powershell
cd D:\progs\sunocleanser
conda env create -f environment.yml
conda activate sunocleanser
python -m sunocleanser.cli path\to\song.wav
```

## GUI

- `sunocleanser-gui.bat` / `sunocleanser-gui.sh` — `conda run` + `python -m sunocleanser.gui` (el `.sh` puede cargar `conda.sh` si conda no está en el PATH)
- O: `conda activate sunocleanser` y `python -m sunocleanser.gui`

Salida por defecto en `out/`. Procesamiento en un hilo aparte para no bloquear la ventana.
