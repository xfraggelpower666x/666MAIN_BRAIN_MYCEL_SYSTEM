import sys
import pytest
from klrw.windows_logical_io import WindowsLogicalDiskSampler, _PdhFmt, PDH_FMT_DOUBLE


def test_linux_requires_windows():
    if sys.platform != 'win32':
        with pytest.raises(OSError):WindowsLogicalDiskSampler()


def test_double_layout_and_flag():
    import ctypes
    assert ctypes.sizeof(_PdhFmt)>=16
    assert PDH_FMT_DOUBLE==512


def test_counter_paths_and_no_windows_profile_hardcode():
    from pathlib import Path
    source=(Path(__file__).parents[1]/'src/klrw/windows_logical_io.py').read_text()
    assert 'LogicalDisk(' in source
    assert 'PdhAddEnglishCounterW' in source
    assert 'C:\\Users' not in source
