"""R03 constants and input contracts."""
from __future__ import annotations
import math

SCHEMA = "research-orchestra/stem-analysis/r03-v1"
ALLOWED_ROLES = ("kick", "bass", "vocal", "acid", "guitar", "fx")
BANDS: tuple[tuple[str, float, float], ...] = (
    ("sub_20_60", 20.0, 60.0),
    ("bass_60_120", 60.0, 120.0),
    ("low_mid_120_250", 120.0, 250.0),
    ("mid_250_500", 250.0, 500.0),
    ("upper_mid_500_2k", 500.0, 2000.0),
    ("presence_2k_5k", 2000.0, 5000.0),
    ("high_5k_10k", 5000.0, 10000.0),
    ("air_10k_20k", 10000.0, 20000.0),
)
FFT_SIZE = 16384
MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 96000
MAX_CHANNELS = 2
MAX_STEMS = 6
MIN_STEMS = 2
MAX_DURATION_SECONDS = 600.0
DURATION_TOLERANCE_SECONDS = 1.0
MAX_TOTAL_INPUT_BYTES = 2 * 1024 * 1024 * 1024
MAX_WORKING_MEMORY_BYTES = 32 * 1024 * 1024
DB_FLOOR = -120.0

class AnalysisError(ValueError):
    """A deterministic input or resource guard blocked analysis."""

def _fail(code: str) -> None:
    raise AnalysisError(code)

def _dbfs(power: float) -> float:
    if not math.isfinite(power) or power <= 0.0:
        return DB_FLOOR
    return max(DB_FLOOR, 10.0 * math.log10(power))

def parse_stem_spec(value: str) -> tuple[str, str]:
    """Parse the explicit role=relative-filename contract; no fuzzy role guessing."""
    if not isinstance(value, str) or "=" not in value:
        _fail("INVALID_STEM_SPEC_EXPECT_ROLE_EQUALS_FILENAME")
    role, filename = value.split("=", 1)
    if role not in ALLOWED_ROLES:
        _fail("UNKNOWN_STEM_ROLE:" + role)
    if not filename or filename.strip() != filename:
        _fail("INVALID_STEM_FILENAME")
    return role, filename
