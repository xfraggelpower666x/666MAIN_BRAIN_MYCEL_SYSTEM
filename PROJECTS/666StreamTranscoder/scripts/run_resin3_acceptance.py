"""Safe R07 test launcher: original 3DX hardware scripts are NOT unittest modules."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("test_resin3_*.py", "test_crossfade_audio.py")


def main():
    for pattern in TARGETS:
        args = [sys.executable, "-m", "unittest", "discover",
                "-s", "tests", "-p", pattern, "-v"]
        print("Testing:", " ".join(args), flush=True)
        status = subprocess.call(args, cwd=ROOT)
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
