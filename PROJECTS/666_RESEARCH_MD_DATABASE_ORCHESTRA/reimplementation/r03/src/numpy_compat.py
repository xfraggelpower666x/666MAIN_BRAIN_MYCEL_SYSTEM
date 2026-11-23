"""Single dependency gate for the numerical FFT backend."""
try:
    import numpy as np
except ImportError as exc:  # fail before reading any user audio
    raise RuntimeError("NUMPY_REQUIRED: install reimplementation/r03/requirements.txt") from exc
